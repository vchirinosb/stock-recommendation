import json
import os

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api.routes import stocks
from app.api.v1.endpoints.stocks import router as stocks_router
from app.services.agents.llm_agent import get_stock_recommendation

app = FastAPI()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')
cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Redis cache timeout in seconds (e.g., 600 seconds = 10 minutes)
CACHE_TIMEOUT = 600

app.include_router(stocks_router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/stocks")


class StockRequest(BaseModel):
    user_input: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/get-chat")
async def get_chat(data: StockRequest):
    try:
        # Check if result for the given user_input is cached
        cached_result = cache.get(data.user_input)

        if cached_result:
            # If cached, return the result from Redis
            return json.loads(cached_result)

        # Otherwise, get the stock recommendation
        result = get_stock_recommendation(data.user_input)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # Cache the result for future requests (serialize as JSON)
        await cache.set(data.user_input, json.dumps(result), ex=CACHE_TIMEOUT)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
