import logging

from langgraph.constants import END
from langgraph.graph import StateGraph
from langsmith import traceable

from app.schemas.agent_state import AgentState
from app.services.chains.stock_generation_chain import (execute_tools,
                                                        run_agent,
                                                        should_continue)
from app.services.tools.stock_tools import tools

logging.basicConfig(level=logging.INFO)


@traceable(name="TransformArticleLLMChain")
def get_stock_recommendation(user_input: str) -> list:
    """
    Get stock recommendations based on user input.

    Args:
        user_input (str): The user's input.

    Returns:
        list: A list of stock recommendations.
    """
    try:
        inputs = {
            "input": user_input,
            "messages": [{"role": "user", "content": user_input}],
            "chat_history": [],
            "intermediate_steps": [],
            "agent_scratchpad": "",
            "tools": ", ".join([tool.name for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
        logging.info(f"Inputs: {inputs}")
        results = []
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", run_agent)
        workflow.add_node("action", execute_tools)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent", should_continue, {"continue": "action", "end": END}
        )
        workflow.add_edge("action", "agent")
        app = workflow.compile()
        for s in app.stream(inputs):
            logging.info(f"Stream result: {s}")
            result = list(s.values())[0]
            results.append(result)
        return results
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return [{"error": str(e)}]
