from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[List, add_messages]
    query: str
    rewritten_query: Optional[str]
    response: Optional[str]
    response_chunk: Optional[str]