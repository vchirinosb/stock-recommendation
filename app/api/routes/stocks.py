from fastapi import APIRouter

from app.services.agents.llm_agent import get_stock_recommendation

router = APIRouter()


@router.post("/recommendation")
def get_recommendation(user_input: str):
    """
    API route to provide stock recommendations based on user input.

    Args:
        user_input (str): Input for stock recommendations, which could be a
        company name, stock symbol.

    Returns:
        JSON: A response containing stock recommendations, usually based on an
        analysis performed by the `get_stock_recommendation` function.
    """
    return get_stock_recommendation(user_input)
