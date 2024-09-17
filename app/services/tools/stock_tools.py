import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from app.core.config import settings


@tool
def call_duck_search(query: str) -> str:
    """
    Search for stock ticker and recent stock-related news using DuckDuckGo.

    Args:
        query (str): Search query to find the stock ticker or news.

    Returns:
        str: Response with the ticker or related news.
    """
    search = DuckDuckGoSearchRun()
    response = search.run(query)
    return response


@tool
def call_get_stock_price(ticker: str) -> str:
    """
    Get historical price data for a given stock ticker.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        str: Response with historical price data.
    """
    url = f"{settings.base_url}/stock-price/{ticker}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching stock price: {str(e)}"


@tool
def call_get_financial_statements(ticker: str) -> str:
    """
    Get financial statements for a given stock ticker.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        str: Response with financial statements.
    """
    url = f"{settings.base_url}/financial-statement/{ticker}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching financial statements: {str(e)}"


@tool
def call_get_recent_stock_news(company_name: str) -> str:
    """
    Get the most recent news related to a company.

    Args:
        company_name (str): Name of the company.

    Returns:
        str: Response with recent news about the company.
    """
    url = f"{settings.base_url}/recent-news/{company_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching recent news: {str(e)}"


tools = [
    call_duck_search,
    call_get_stock_price,
    call_get_financial_statements,
    call_get_recent_stock_news,
]
