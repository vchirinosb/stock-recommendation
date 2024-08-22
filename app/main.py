import yfinance as yf
from api.v1.endpoints.stocks import router as stocks_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(stocks_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Hello": "World"}

