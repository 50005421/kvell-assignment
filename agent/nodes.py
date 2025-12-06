from typing import TypedDict, Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent, AgentState

from agent.llm import ollamaLlm
from agent.prompts import get_validator_system_prompt, get_supervisor_system_prompt, get_converse_system_prompt
from agent.tools import STRING_TOOLS, CALCULATOR_TOOLS

calculator_agent = create_agent(ollamaLlm, tools=CALCULATOR_TOOLS)
string_agent = create_agent(ollamaLlm, tools=STRING_TOOLS)


def calculator_node(state: AgentState):
    result = calculator_agent.invoke(state)
    return {
        "messages": [AIMessage(content=result["messages"][-1].content, name="Calculator_Agent")]
    }

def string_node(state: AgentState):
    result = string_agent.invoke(state)
    return {
        "messages": [AIMessage(content=result["messages"][-1].content, name="String_Agent")]
    }

def converse_node(state: AgentState):
    messages = state['messages']
    last_message = messages[-1].content
    response = ollamaLlm.invoke([SystemMessage(content=get_converse_system_prompt()),HumanMessage(content=last_message)])
    return {"messages": [AIMessage(content=response.content, name="Converse_Agent")]}

def validator_node(state: AgentState):
    messages = state['messages']
    last_message = messages[-1].content
    validation_prompt = get_validator_system_prompt(last_message)
    response = ollamaLlm.invoke([HumanMessage(content=validation_prompt)])
    return {"messages": [AIMessage(content=response.content, name="Validator_Agent")]}


class Router(TypedDict):
    """Worker to route to next or text. If no workers needed, route to Validator."""
    next: Literal["Calculator_Agent", "String_Agent", "Validator_Agent", "Converse_Agent"]

def supervisor_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_supervisor_system_prompt()),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Who should act next? Select one of: Calculator_Agent, String_Agent, Validator_Agent, Converse_Agent")
    ])

    supervisor_chain = prompt | ollamaLlm.with_structured_output(Router)
    result = supervisor_chain.invoke(state)
    return {"next": result["next"]}
