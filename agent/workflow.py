from langchain.agents import AgentState
from langgraph.graph import StateGraph, START, END

from agent.nodes import supervisor_node, calculator_node, string_node, validator_node, converse_node


def create_agent_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("Calculator_Agent", calculator_node)
    workflow.add_node("String_Agent", string_node)
    workflow.add_node("Validator_Agent", validator_node)
    workflow.add_node("Converse_Agent", converse_node)


    workflow.add_edge(START, "Supervisor")


    workflow.add_conditional_edges(
        "Supervisor",
        lambda x: x["next"],
        {
            "Calculator_Agent": "Calculator_Agent",
            "String_Agent": "String_Agent",
            "Validator_Agent": "Validator_Agent",
            "Converse_Agent": "Converse_Agent"
        }
    )

    workflow.add_edge("Calculator_Agent", "Supervisor")
    workflow.add_edge("String_Agent", "Supervisor")
    workflow.add_edge("Validator_Agent", END)
    workflow.add_edge("Converse_Agent", END)

    return workflow.compile()