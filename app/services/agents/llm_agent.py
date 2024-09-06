from app.services.chains.stock_generation_chain import app
from app.services.tools.stock_tools import tools


def get_stock_recommendation(user_input: str):
    try:
        inputs = {
            "input": user_input,  # Ensure 'input' is provided
            "messages": [{"role": "user", "content": user_input}],
            "chat_history": [],
            "intermediate_steps": [],  # Initialize if required
            "agent_scratchpad": "",    # Initialize if required
            "tools": ", ".join([tool.name for tool in tools]),  # Ensure tools and tool_names are included
            "tool_names": ", ".join([tool.name for tool in tools])
        }
        results = []
        for s in app.stream(inputs):
            result = list(s.values())[0]
            print("Result: ", result)
            results.append(result)
        return results
    except Exception as e:
        return {"error": str(e)}

