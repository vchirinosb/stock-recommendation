from langchain.agents import create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.prebuilt.chat_agent_executor import AgentState

from app.services.tools.stock_tools import tools

model = ChatOllama(model='llama3.1:8b')


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
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    tools=tools,
    tool_names=tool_names,
)

agent_runnable = create_react_agent(
    llm=model,
    prompt=prompt_template,
    tools=tools,
)

def execute_tools(state):
    print(f"State before execute_tools: {state}")
    messages = [state.get("agent_outcome", "No outcome")]
    last_message = messages[-1]

    tool_name = last_message.tool

    print(f"Calling tool: {tool_name}")

    action = ToolInvocation(
        tool=tool_name,
        tool_input=last_message.tool_input,
    )
    response = tool_executor.invoke(action)

    intermediate_steps = state.get("intermediate_steps", [])
    intermediate_steps.append((last_message, response))

    print(f"State after execute_tools: {state}")

    return {"intermediate_steps": intermediate_steps}


def run_agent(state):
    if "intermediate_steps" not in state:
        state["intermediate_steps"] = []
    if "agent_scratchpad" not in state:
        state["agent_scratchpad"] = ""  # Initialize if missing
    if "input" not in state:
        state["input"] = ""  # Initialize if missing

    agent_outcome = agent_runnable.invoke(state)
    return {
        "agent_outcome": agent_outcome,
        "intermediate_steps": state["intermediate_steps"],
        "agent_scratchpad": state["agent_scratchpad"],
        "input": state["input"]
    }


def should_continue(state):
    messages = [state.get("agent_outcome", "No outcome")]
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
