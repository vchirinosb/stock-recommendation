import operator
from typing import Annotated, TypedDict, Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    messages: Annotated[list[AnyMessage], add_messages]
