import requests

from app.core.config import settings


def call_get_stock_price(ticker: str) -> str:
    url = f"{settings.base_url}/stock-price/{ticker}"
    response = requests.get(url)
    return response.text

def call_get_financial_statements(ticker: str) -> str:
    url = f"{settings.base_url}/financial-statement/{ticker}"
    response = requests.get(url)
    return response.text

def call_get_recent_stock_news(company_name: str) -> str:
    url = f"{settings.base_url}/recent-news/{company_name}"
    response = requests.get(url)
    return response.text
