import requests
from langchain.agents import create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from app.core.config import settings
from app.schemas.agent_state import AgentState

model = ChatOllama(model='llama3.1:8b')

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

tool_executor = ToolExecutor(tools)

# Define prompt template
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

agent_runnable = create_react_agent(
    llm=model,
    prompt=prompt_template,
    tools=tools,
)

def execute_tools(state):
    print("Called `execute_tools`")
    messages = [state["agent_outcome"]]
    last_message = messages[-1]

    tool_name = last_message.tool

    print(f"Calling tool: {tool_name}")

    action = ToolInvocation(
        tool=tool_name,
        tool_input=last_message.tool_input,
    )
    response = tool_executor.invoke(action)
    return {"intermediate_steps": [(state["agent_outcome"], response)]}


def run_agent(state):
    """
    #if you want to better manages intermediate steps
    inputs = state.copy()
    if len(inputs['intermediate_steps']) > 5:
        inputs['intermediate_steps'] = inputs['intermediate_steps'][-5:]
    """
    agent_outcome = agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}


def should_continue(state):
    messages = [state["agent_outcome"]]
    last_message = messages[-1]
    if "Action" not in last_message.log:
        return "end"
    else:
        return "continue"


workflow = StateGraph(AgentState)

workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)


workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)


workflow.add_edge("action", "agent")
app = workflow.compile()


def get_stock_recommendation(user_input: str):
    """
    Obtener la recomendación de stock basado en el input del usuario.

    Args:
        user_input (str): Stock ticker o query.

    Returns:
        dict: Response desde el agente.
    """
    try:
        inputs = {"input": user_input, "chat_history": []}
        results = []
        for s in app.stream(inputs):
            result = list(s.values())[0]
            results.append(result)
            print(result)
        print("response:", results)
        return results
    except Exception as e:
        print("ccccccccccccc")
        return {"error": str(e)}
