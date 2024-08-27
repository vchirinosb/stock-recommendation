import ollama
import requests
from langchain.agents import create_react_agent
from langchain_community.llms.ollama import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

from app.core.config import settings

model = 'llama3.1:8b'
ollama.pull(model)


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


llm = Ollama(model=model)

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

stock_prompt = """
    You are a financial advisor. Give stock recommendations for the given query.
    Answer the following questions as best you can using the following tools:

    {tools}

    {tool_names}

    Steps:
    1) Identify the company name and find the stock ticker. Output the ticker or "This stock does not exist".
    2) Use "Get Stock Historical Price" tool to gather stock info. Output stock data.
    3) Retrieve the company's financial data using "Get Financial Statements". Output financial statement.
    4) Use "Get Recent News" to get the latest stock-related news. Output stock news.
    5) Analyze the stock and provide a recommendation (Buy, Hold, Sell) with justification.

    Format:
    Question: {input}
    Thought: {agent_scratchpad}
"""

tool_names = ", ".join([tool.name for tool in tools])
prompt_template = PromptTemplate(
    template=stock_prompt,
    input_variables=["input", "tools", "tool_names"],
    tools=tools,
    tool_names=tool_names,
)

zero_shot_agent = create_react_agent(
    llm=llm,
    prompt=prompt_template,
    tools=tools,
)

def get_stock_recommendation(user_input: str):
    """
    Obtener la recomendación de stock basado en el input del usuario.

    Args:
        user_input (str): Stock ticker o query.

    Returns:
        dict: Response desde el agente.
    """
    try:
        response = zero_shot_agent.invoke(
            {
                "input": user_input,
                "intermediate_steps": []
            }
        )
        return response
    except Exception as e:
        return {"error": str(e)}
