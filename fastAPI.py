from fastapi import FastAPI, HTTPException, Path
from enum import Enum
from typing import Annotated
import uvicorn
import requests

LISTING = 'top'  # controversial, best, hot, new, random, rising, top


# timeframe enum
class TimeFrame(str, Enum):
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    year = "year"
    all = "all"


# initialize FastAPI
app = FastAPI()


# FastApi get wrapper function
@app.get("/reddit")
async def root(subreddit: str, limit: Annotated[int, Path(gt=0)] = 10,
               timeframe: TimeFrame = "month"):
    data = get_reddit(subreddit, limit, timeframe)
    return get_relevant_data(data)


# http get request
def get_reddit(subreddit, limit, timeframe):
    base_url = f'https://www.reddit.com/r/{subreddit}/{LISTING}.json?limit={limit}&t={timeframe}'
    request = requests.get(base_url, headers={'User-agent': 'yourbot'})
    if not request:
        raise HTTPException(status_code=404, detail="Item not found")
    elif request.status_code == 500:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    elif request.status_code == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    elif request.status_code == 403:
        raise HTTPException(status_code=403, detail="Access Forbidden")
    elif request.status_code == 422:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    return request.json()


# filter only the relevant data from the json
def get_relevant_data(json):
    top_posts_relevant_data = {}
    for post in json['data']['children']:
        top_posts_relevant_data[post['data']['title']] = {"url": post['data']['url'], "score": post['data']['score'],
                                                          "author": post['data']['author_fullname'],
                                                          "number of comments": post['data']['num_comments']}
    return top_posts_relevant_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
