from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from workflow import Workflow
import json

app = FastAPI(title="Chatbot API", description="Streaming chatbot with LLM integration")
workflow = Workflow()

class ChatRequest(BaseModel):
    query: str
    messages: list = []


@app.post("/chat/stream")
async def stream_chat_sse(request: ChatRequest):
    """Stream chat responses using Server-Sent Events (testable in Swagger)"""
    initial_state = {
        "messages": request.messages,
        "query": request.query,
        "rewritten_query": None,
        "response": None,
    }
    
    async def generate():
        try:
            async for chunk in workflow.run_streaming(initial_state):
                if chunk:
                    # Format as SSE
                    data = json.dumps({"chunk": chunk})
                    yield f"data: {data}\n\n"
            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


