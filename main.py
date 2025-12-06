from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent.workflow import create_agent_graph
from modal import ChatRequest, StepLog, ChatResponse

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        agent_graph = create_agent_graph()
        messages = [HumanMessage(content=request.query)]
        final_state = agent_graph.invoke({"messages": messages})
        steps_log = []
        all_messages = final_state["messages"]
        final_answer = ""

        for msg in all_messages:
            if isinstance(msg, AIMessage):
                name = getattr(msg, "name", "Assistant") or "Assistant"
                if name != "Validator_Agent":
                    final_answer = msg.content
                    steps_log.append(
                        StepLog(type="final_answer", content=msg.content, name=name)
                    )
                else:
                    steps_log.append(
                        StepLog(type="thought", content=msg.content, name=name)
                    )
            elif isinstance(msg, ToolMessage):
                steps_log.append(
                    StepLog(type="tool_result", content=str(msg.content), name=msg.name)
                )

        return ChatResponse(response=final_answer or "Process complete.", steps=steps_log)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

