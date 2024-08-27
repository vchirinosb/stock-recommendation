from fastapi import APIRouter

from app.workflow.agent_workflow import get_stock_recommendation

router = APIRouter()

@router.post("/recommendation")
def get_recommendation(user_input: str):
    """
    API route to get stock recommendation.
    """
    return get_stock_recommendation(user_input)
