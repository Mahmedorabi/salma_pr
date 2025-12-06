# from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from models import State
from prompts import *
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


# llm = ChatOllama(
#     model='gemma3:latest',
#     temperature=0.0,
# )

llm = ChatOpenAI(
    model_name='gpt-4o-mini',
    temperature=0.2,
)

def rewrite_query_agent(state: State) -> str:
    user_input = state.get('query')
    messages = state.get('messages', [])

    messages = [
        SystemMessage(content=REWRITE_QUERY_PROMPT),
        HumanMessage(content=query_rewrite_extend(user_input, messages))
    ]

    response = llm.invoke(messages)
    rewritten_query = response.content.strip()
    return {
        "rewritten_query": rewritten_query
    }

async def response_agent(state: State) -> str:
    rewritten_query = state.get('rewritten_query')
    messages = state.get('messages', [])

    chat_history_str = formmated_history(messages)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=system_prompt_extend(rewritten_query, chat_history_str))
    ]
    full_response = ""
    async for chunck in llm.astream(messages):
        if hasattr(chunck, 'content') and chunck.content:
            full_response += chunck.content
    return {
        "response": full_response.strip()
    }

async def streaming_response_agent(state: State):
    rewritten_query = state.get('rewritten_query')
    messages = state.get('messages', [])

    chat_history_str = formmated_history(messages)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=system_prompt_extend(rewritten_query, chat_history_str))
    ]
    
    async for chunk in llm.astream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            yield {
                "response_chunk": chunk.content
            }