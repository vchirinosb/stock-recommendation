from app.services.chains.stock_generation_chain import app
from app.services.tools.stock_tools import tools
from langsmith import traceable


@traceable(name="TransformArticleLLMChain")
def get_stock_recommendation(user_input: str):
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
        print(f"Inputs: {inputs}")
        results = []
        for s in app.stream(inputs):
            print(f"Stream result: {s}")
            result = list(s.values())[0]
            results.append(result)
        return results
    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"error": str(e)}
