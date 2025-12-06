# kvell-assignment

Multi-agent chat application built with FastAPI, LangGraph, LangChain, and Ollama.

The project exposes a `/chat` API that routes user queries through a small team of agents:

- **Supervisor** – decides which specialized agent should act next.
- **Calculator_Agent** – performs arithmetic using calculator tools.
- **String_Agent** – performs string manipulation operations.
- **Converse_Agent** – handles general conversation and Q&A.
- **Validator_Agent** – evaluates the final answer for quality and correctness.

A simple Streamlit UI is included to chat with the agents and to visualize each step in the workflow.

## Tech stack

- **Backend:** FastAPI
- **Agent orchestration:** LangGraph + LangChain agents
- **LLM:** Ollama via `langchain-ollama` (`granite4:micro` model)
- **Frontend:** Streamlit
- **Data models:** Pydantic

## Project structure

- `main.py` – FastAPI app exposing the `/chat` endpoint.
- `modal.py` – Pydantic models for request/response (`ChatRequest`, `ChatResponse`, `StepLog`).
- `streamlit_app.py` – Streamlit frontend to interact with the backend and inspect agent steps.
- `agent/llm.py` – Ollama `ChatOllama` client configuration.
- `agent/tools.py` – Calculator and string manipulation tools exposed to agents.
- `agent/prompts.py` – System prompts for Supervisor, Converse, and Validator agents.
- `agent/nodes.py` – Node functions for each agent and the router used in the graph.
- `agent/state.py` – Shared `AgentState` definition for LangGraph.
- `agent/workflow.py` – Construction and compilation of the agent StateGraph.
- `requirements.txt` – Python dependencies.

## Prerequisites

- Python 3.10+ (recommended)
- [Ollama](https://ollama.com/) installed and running locally
- The `granite4:micro` model pulled in Ollama, e.g.:

  ```bash path=null start=null
  ollama pull granite4:micro
  ```

## Setup

1. **Create and activate a virtual environment (optional but recommended):**

   ```bash path=null start=null
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash path=null start=null
   pip install -r requirements.txt
   ```

## Running the backend (FastAPI)

Start the FastAPI app with Uvicorn:

```bash path=null start=null
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will expose the `/chat` endpoint at `http://localhost:8000/chat`.

### `/chat` endpoint

- **Method:** `POST`
- **URL:** `/chat`
- **Request body (`ChatRequest`):**

  ```json path=null start=null
  {
    "query": "Your question or instruction",
    "history": [
      { "role": "user", "content": "previous user message" },
      { "role": "assistant", "content": "previous assistant reply" }
    ]
  }
  ```

- **Response (`ChatResponse`):**

  ```json path=null start=null
  {
    "response": "final answer from the agents",
    "steps": [
      {
        "type": "final_answer" | "thought" | "tool_result",
        "content": "...",
        "name": "Calculator_Agent" | "String_Agent" | "Converse_Agent" | "Validator_Agent" | "Assistant"
      }
    ]
  }
  ```

The backend constructs a LangGraph state graph in `agent/workflow.py` and invokes it once per request. As messages are produced by each agent and by tools, they are collected and transformed into a human-readable `steps` log.

## Running the Streamlit UI

In a separate terminal (with the same virtual environment active), run:

```bash path=null start=null
streamlit run streamlit_app.py
```

By default, the app expects the backend to be available at `http://localhost:8000` (see `BACKEND_URL` in `streamlit_app.py`). If you change the backend port or host, update that constant accordingly.

### UI features

- Text input box for entering your query.
- Streaming-style display of the assistant’s answer.
- Sidebar controls to clear the conversation.
- A dedicated panel showing each agent/tool step and the validator’s evaluation.

## How the agents work (high level)

1. The **Supervisor** inspects the conversation state and decides which agent should act next, choosing from:
   - `Calculator_Agent`
   - `String_Agent`
   - `Validator_Agent`
   - `Converse_Agent`
2. Specialized agents call tools defined in `agent/tools.py` when needed.
3. Once the user’s task appears complete, the Supervisor routes to **Validator_Agent**, which evaluates the final answer according to a structured prompt.
4. The FastAPI endpoint aggregates all messages, returning the final answer and a detailed step log for visualization in the UI.

## Development notes

- To change the underlying LLM or its parameters, edit `agent/llm.py`.
- To add more tools, extend `agent/tools.py` and wire them into new or existing agents in `agent/nodes.py`.
- To modify routing logic or add new agents, update the supervisor prompt in `agent/prompts.py` and the graph in `agent/workflow.py`.
