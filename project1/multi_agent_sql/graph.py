"""
LangGraph workflow definition for the multi-agent customer service system.
Defines the graph structure, nodes, edges, and routing logic.
"""

from langgraph.graph import StateGraph, END
from typing import Any

try:
    from state_schema import CustomerServiceState
    from agents import (
        classification_agent,
        query_agent,
        sales_agent,
        refund_agent,
        analytics_agent,
        supervisor_agent,
        clarification_agent,
        human_handoff_agent,
    )
    from routing import route_to_specialist, check_if_complete
except ImportError:
    from .state_schema import CustomerServiceState
    from .agents import (
        classification_agent,
        query_agent,
        sales_agent,
        refund_agent,
        analytics_agent,
        supervisor_agent,
        clarification_agent,
        human_handoff_agent,
    )
    from .routing import route_to_specialist, check_if_complete


def create_graph():
    """
    Create and compile the LangGraph workflow.

    Returns:
        Compiled graph instance ready for execution
    """

    # Create state graph
    workflow = StateGraph(CustomerServiceState)

    # ==================== ADD NODES ====================
    print("Adding nodes to graph...")

    workflow.add_node("classification_agent", classification_agent)
    workflow.add_node("query_agent", query_agent)
    workflow.add_node("sales_agent", sales_agent)
    workflow.add_node("refund_agent", refund_agent)
    workflow.add_node("analytics_agent", analytics_agent)
    workflow.add_node("supervisor_agent", supervisor_agent)
    workflow.add_node("clarification_agent", clarification_agent)
    workflow.add_node("human_handoff", human_handoff_agent)

    # ==================== SET ENTRY POINT ====================
    print("Setting entry point...")
    workflow.set_entry_point("classification_agent")

    # ==================== ADD CONDITIONAL EDGES ====================
    print("Adding conditional edges...")

    # From classification, route to specialist
    workflow.add_conditional_edges(
        "classification_agent",
        route_to_specialist,
        {
            "query_agent": "query_agent",
            "sales_agent": "sales_agent",
            "refund_agent": "refund_agent",
            "analytics_agent": "analytics_agent",
            "clarification_agent": "clarification_agent",
        }
    )

    # From clarification, return to classification
    workflow.add_edge("clarification_agent", "classification_agent")

    # From specialist agents, check if complete
    for agent in ["query_agent", "sales_agent", "refund_agent", "analytics_agent"]:
        workflow.add_conditional_edges(
            agent,
            check_if_complete,
            {
                "supervisor_agent": "supervisor_agent",
                "classification_agent": "classification_agent",
                "human_handoff": "human_handoff"
            }
        )

    # From supervisor to end
    workflow.add_edge("supervisor_agent", END)

    # From human handoff to end
    workflow.add_edge("human_handoff", END)

    # Compile the graph
    print("Compiling graph...")
    app = workflow.compile()

    return app


def visualize_graph(app: Any) -> str:
    """
    Generate a visualization of the graph in Mermaid format.

    Args:
        app: Compiled graph instance

    Returns:
        Mermaid diagram string
    """
    return app.get_graph().to_mermaid()
