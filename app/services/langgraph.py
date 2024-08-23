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
    You are a financial advisor. Give stock recommendations for given query.
    Everytime first you should identify the company name and get the stock ticker symbol for the stock.
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    {tool_names}

    steps-
    Note- if you fail in satisfying any of the step below, Just move to next one
    1) Get the company name and search for the "company name + stock ticker" on internet. Dont hallucinate extract stock ticker as it is from the text. Output- stock ticker. If stock ticker is not found, stop the process and output this text: This stock does not exist
    2) Use "Get Stock Historical Price" tool to gather stock info. Output- Stock data
    3) Get company's historic financial data using "Get Financial Statements". Output- Financial statement
    4) Use this "Get Recent News" tool to search for latest stock related news. Output- Stock news
    5) Analyze the stock based on gathered data and give detailed analysis for investment choice. provide numbers and reasons to justify your answer. Output- Give a single answer if the user should buy,hold or sell. You should Start the answer with Either Buy, Hold, or Sell in Bold after that Justify.

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do, Also try to follow steps mentioned above
    Action: the action to take, should be one of [Get Stock Historical Price, Stock Ticker Search, Get Recent News, Get Financial Statements]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times, if Thought is empty go to the next Thought and skip Action/Action Input and Observation)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
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


if __name__ == "__main__":
    user_input = "APPL"

    try:
        response = zero_shot_agent.invoke({"input": user_input, "intermediate_steps": []})
        print(response)
    except Exception as e:
        print(f"Error running the agent: {e}")
