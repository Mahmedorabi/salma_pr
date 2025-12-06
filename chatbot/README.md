# AI Chatbot with LangGraph Workflow

A modern streaming chatbot API built with FastAPI, LangGraph, and OpenAI's GPT models. This project implements a sophisticated conversational AI system with query rewriting capabilities and real-time streaming responses.

## 🚀 Features

- **Streaming Responses**: Real-time response streaming using Server-Sent Events (SSE)
- **Query Rewriting**: Intelligent query enhancement for better context understanding
- **LangGraph Workflow**: Modular agent-based architecture for extensible conversation flow
- **FastAPI Backend**: High-performance async API with automatic documentation
- **OpenAI Integration**: Powered by GPT-4o-mini for intelligent conversations
- **Chat History**: Maintains conversation context across multiple interactions

## 🏗️ Architecture

The chatbot uses a workflow-based architecture with the following components:

### Core Components
- **Workflow Engine**: Orchestrates the conversation flow using LangGraph
- **Rewrite Query Agent**: Enhances user queries for better understanding
- **Response Agent**: Generates contextual responses with streaming support
- **State Management**: Maintains conversation state and message history

### Agent Pipeline
1. **Query Rewriting**: Analyzes and enhances user input
2. **Response Generation**: Creates intelligent, context-aware responses
3. **Streaming Output**: Delivers responses in real-time chunks

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **AI Orchestration**: LangGraph
- **Language Model**: OpenAI GPT-4o-mini
- **Language Processing**: LangChain
- **Environment Management**: Python-dotenv
- **API Documentation**: Swagger UI (auto-generated)

## 📁 Project Structure

```
chatbot/
├── app.py          # FastAPI application and endpoints
├── workflow.py     # LangGraph workflow definition
├── agents.py       # AI agents (query rewriter, response generator)
├── models.py       # Pydantic models and state definitions
├── prompts.py      # System prompts and templates
└── __pycache__/    # Python cache files
```

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chatbot
```

2. Install dependencies:
```bash
pip install fastapi langchain-openai langchain-core langgraph python-dotenv uvicorn
```

3. Set up environment variables:
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

4. Run the application:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### API Usage

#### Streaming Chat Endpoint
```http
POST /chat/stream
Content-Type: application/json

{
  "query": "What is machine learning?",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you today?"}
  ]
}
```

#### Response Format (SSE)
```javascript
data: {"chunk": "Machine learning is"}
data: {"chunk": " a subset of artificial intelligence"}
data: {"chunk": " that enables computers to learn"}
data: {"done": true}
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Model Configuration
The system uses GPT-4o-mini by default. To change the model, modify the `llm` configuration in `agents.py`:

```python
llm = ChatOpenAI(
    model_name='gpt-4o-mini',  # Change model here
    temperature=0.2,           # Adjust creativity
)
```

## 🧪 Testing

Test the streaming endpoint using curl:
```bash
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"query": "Tell me about AI", "messages": []}'
```

## 📈 Performance Features

- **Async Operations**: Non-blocking request handling
- **Streaming Responses**: Reduced perceived latency
- **Efficient State Management**: Optimized memory usage
- **Error Handling**: Comprehensive error reporting

## 🛡️ Security Considerations

- Environment variable management for API keys
- CORS headers configured for cross-origin requests
- Input validation with Pydantic models

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using modern AI and web technologies**