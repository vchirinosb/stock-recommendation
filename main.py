from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api.routes import stocks
from app.api.v1.endpoints.stocks import router as stocks_router
from app.workflow.agent_workflow import get_stock_recommendation

app = FastAPI()

app.include_router(stocks_router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/stocks")


class StockRequest(BaseModel):
    user_input: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/get-chat")
async def get_chat(data: StockRequest):
    result = get_stock_recommendation(data.user_input)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
