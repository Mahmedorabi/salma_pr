from agents import *
from models import State
from langgraph.graph import StateGraph, START, END

class Workflow:
    def __init__(self):
        self.rewrite_query_agent = rewrite_query_agent
        self.response_agent = response_agent

    def _build_graph(self):
        graph = StateGraph(State)

        graph.add_node("rewrite_query_agent", self.rewrite_query_agent)
        graph.add_node("response_agent", self.response_agent)

        graph.add_edge(START, "rewrite_query_agent")
        graph.add_edge("rewrite_query_agent", "response_agent")
        graph.add_edge("response_agent", END)
        return graph.compile()
    
    async def run(self, initial_state: State):
        graph = self._build_graph()
        async for event in graph.astream(initial_state):
            if 'response_agent' in event:
                yield event['response_agent']['response']
    
    async def run_streaming(self, initial_state: State):
        # First run the rewrite query agent
        rewritten_state = self.rewrite_query_agent(initial_state)
        updated_state = {**initial_state, **rewritten_state}
        
        async for chunk in streaming_response_agent(updated_state):
            if 'response_chunk' in chunk:
                yield chunk['response_chunk']

