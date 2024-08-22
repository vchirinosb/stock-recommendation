import yfinance as yf
from fastapi import FastAPI

from api.v1.endpoints.stocks import router as stocks_router

app = FastAPI()

app.include_router(stocks_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Hello": "World"}

