import requests
from langchain.agents import initialize_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool

from app.core.config import settings


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
    Tool(
        name="Stock Ticker Search",
        func=lambda query: DuckDuckGoSearchRun().run(query),
        description="Use only when you need to get stock ticker from internet, you can also get recent stock related news. Don't use it for any other analysis or task"
    ),
    Tool(
        name="Get Stock Historical Price",
        func=call_get_stock_price,
        description="Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the stock ticker to it"
    ),
    Tool(
        name="Get Recent News",
        func=call_get_recent_stock_news,
        description="Use this to fetch recent news about stocks"
    ),
    Tool(
        name="Get Financial Statements",
        func=call_get_financial_statements,
        description="Use this to get financial statement of the company. With the help of this data company's historic performance can be evaluated. You should input stock ticker to it"
    )
]

zero_shot_agent = initialize_agent(
    llm=llama_generate,
    agent="zero-shot-react-description",
    tools=tools,
    verbose=True,
    max_iteration=4,
    return_intermediate_steps=False,
    handle_parsing_errors=True
)

stock_prompt = """
Eres un asesor financiero. Da recomendaciones de inversión para la consulta dada.
...
"""
zero_shot_agent.agent.llm_chain.prompt.template = stock_prompt