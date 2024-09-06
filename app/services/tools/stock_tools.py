import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from app.core.config import settings


@tool
def call_duck_search(query):
    """
    Stock Ticker Search.
    Use only when you need to get stock ticker from internet, you can also get
    recent stock related news. Don't use it for any other analysis or task.

    Args:
        query (str): query.

    Returns:
        str: Response with the ticker

    """
    return DuckDuckGoSearchRun().run(query)

@tool
def call_get_stock_price(ticker):
    """
    Obtener el precio histórico de un ticker.

    Args:
        ticker (str): Ticker a consultar.

    Returns:
        str: Response con los datos del precio histórico del ticker.
    """
    url = f"{settings.base_url}/stock-price/{ticker}"
    response = requests.get(url)
    return response.text

@tool
def call_get_financial_statements(ticker):
    """
    Obtener los estados financieros de un ticker.

    Args:
        ticker (str): Ticker a consultar.

    Returns:
        str: Response con los estados financieros del ticker.
    """
    url = f"{settings.base_url}/financial-statement/{ticker}"
    response = requests.get(url)
    return response.text

@tool
def call_get_recent_stock_news(company_name):
    """
    Obtener las noticias más recientes relacionadas con una empresa.

    Args:
        company_name (str): Nombre de la empresa a consultar.

    Returns:
        str: Response con las noticias más recientes sobre la empresa.
    """
    url = f"{settings.base_url}/recent-news/{company_name}"
    response = requests.get(url)
    return response.text


tools = [
    call_duck_search,
    call_get_stock_price,
    call_get_financial_statements,
    call_get_recent_stock_news,
]

