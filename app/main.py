from api.v1.endpoints.stocks import router as stocks_router
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

app.include_router(stocks_router, prefix="/api/v1")


class StockRequest(BaseModel):
    user_input: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/get-recommendation")
async def get_stock_recommendation(request: StockRequest):
    try:
        # Call the zero_shot_agent from langgraph.py and return the response
        # response = zero_shot_agent.invoke({
        #    "input": request.user_input,
        #    "intermediate_steps": []
        # })
        # return {"response": response}
        return {"response": ""}
    except Exception as e:
        return {"error": str(e)}
