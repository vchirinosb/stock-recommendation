import logging

from langchain.agents import create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.prebuilt.chat_agent_executor import AgentState

from app.services.tools.stock_tools import tools

logging.basicConfig(level=logging.INFO)

model = ChatOllama(model='llama3.1:8b')
tool_executor = ToolExecutor(tools)

# Define prompt template
stock_prompt = """
    You are a financial advisor tasked with providing stock recommendations based on the following query. Use the available tools to guide your analysis.

    Tools available: {tools}

    ### Steps:
    Follow these steps in order, and if any step fails, proceed to the next:

    1. **Identify** the company name and retrieve the stock ticker. If no ticker is found, return "This stock does not exist."
    2. **Fetch** historical stock prices using the "Get Stock Historical Price" tool.
    3. **Obtain** the company's financial statements via the "Get Financial Statements" tool.
    4. **Retrieve** the latest stock-related news using the "Get Recent News" tool.
    5. **Analyze** all data and provide a recommendation (Buy, Hold, Sell) with a clear justification.

    ### Response Format:
    Question: {input}
    Thought: {agent_scratchpad}
    Thought: Reflect on the necessary action, following the steps above.
    Action: Select a tool from {tool_names}
    Action Input: Specify the input for the selected action
    Observation: Provide the result of the action (DO NOT include any code)

    (Repeat the Thought/Action/Observation cycle as needed)

    Thought: I have the final answer
    Final Answer: Provide your conclusion and recommendation
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


class ToolExecutionError(Exception):
    """Custom exception for tool execution errors."""
    pass


def execute_tools(state):
    print(f"State before execute_tools: {state}")

    # Extract the last message from state['messages']
    messages = state.get("messages", [])

    if not messages:
        raise ToolExecutionError("No messages found to execute tools.")

    # Get the last message (assuming it's an AIMessage-like object)
    last_message = messages[-1]

    # Accessing tool name directly, assuming 'last_message' has a 'tool' attribute
    if not hasattr(last_message, 'tool'):
        raise ToolExecutionError("No tool specified in the last message.")

    tool_name = last_message.tool

    # Perform the tool invocation
    action = ToolInvocation(
        tool=tool_name,
        tool_input=last_message.tool_input  # Accessing tool_input directly
    )
    response = tool_executor.invoke(action)

    # Append the result (observation) to the intermediate steps
    intermediate_steps = state.get("intermediate_steps", [])
    intermediate_steps.append((last_message, response))

    # Append the observation message (adjust according to actual message structure)
    messages.append({
        "role": "tool",  # Assuming this is a tool's response
        "content": f"Observation: {response}"
    })

    # Return updated state
    return {"intermediate_steps": intermediate_steps, "messages": messages}


def run_agent(state):
    if "intermediate_steps" not in state:
        state["intermediate_steps"] = []
    if "agent_scratchpad" not in state:
        state["agent_scratchpad"] = ""  # Initialize if missing
    if "input" not in state:
        state["input"] = ""  # Initialize if missing

    # Ensure we have a 'messages' key to store the agent output
    if "messages" not in state:
        state["messages"] = []

    # Run the agent and get the outcome
    agent_outcome = agent_runnable.invoke(state)

    # Ensure agent_outcome is an AIMessage-like object and add it to 'messages'
    state["messages"].append({
        "role": "assistant",  # Assuming this is the assistant's response
        "content": f"Action: {agent_outcome.tool}\nAction Input: {agent_outcome.tool_input}\n{agent_outcome.log}"
    })

    return {
        "agent_outcome": agent_outcome,
        "intermediate_steps": state["intermediate_steps"],
        "agent_scratchpad": state["agent_scratchpad"],
        "input": state["input"],
        "messages": state["messages"],  # Ensure messages are passed along
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
