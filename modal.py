from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    history: List[dict] = []

class StepLog(BaseModel):
    type: str
    content: str
    name: str = ""

class ChatResponse(BaseModel):
    response: str
    steps: List[StepLog]