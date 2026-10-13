"""
LangGraph workflow definition for the agentic RAG system.
Defines the graph structure, nodes, edges, and routing logic.
"""

from langgraph.graph import StateGraph, END
from typing import Any

try:
    from state_schema import RAGState
    from agents import (
        classification_agent,
        retrieval_agent,
        generation_agent,
        supervisor_agent,
        clarification_agent,
    )
    from routing import route_after_classification, check_if_complete
except ImportError:
    from .state_schema import RAGState
    from .agents import (
        classification_agent,
        retrieval_agent,
        generation_agent,
        supervisor_agent,
        clarification_agent,
    )
    from .routing import route_after_classification, check_if_complete


def create_graph():
    """
    Create and compile the LangGraph workflow.

    Graph Flow:
    START → classification_agent → [conditional routing]
      ├─ simple/complex → retrieval_agent → generation_agent → [check_if_complete]
      │                                                          ├─ complete → supervisor_agent → END
      │                                                          └─ not complete → clarification_agent → END
      └─ unclear → clarification_agent → END

    Returns:
        Compiled graph instance ready for execution
    """

    # Create state graph
    workflow = StateGraph(RAGState)

    # ==================== ADD NODES ====================
    print("Adding nodes to graph...")

    workflow.add_node("classification_agent", classification_agent)
    workflow.add_node("retrieval_agent", retrieval_agent)
    workflow.add_node("generation_agent", generation_agent)
    workflow.add_node("supervisor_agent", supervisor_agent)
    workflow.add_node("clarification_agent", clarification_agent)

    # ==================== SET ENTRY POINT ====================
    print("Setting entry point...")
    workflow.set_entry_point("classification_agent")

    # ==================== ADD CONDITIONAL EDGES ====================
    print("Adding conditional edges...")

    # From classification, route based on query type
    workflow.add_conditional_edges(
        "classification_agent",
        route_after_classification,
        {
            "retrieval_agent": "retrieval_agent",
            "clarification_agent": "clarification_agent"
        }
    )

    # From retrieval, always go to generation
    workflow.add_edge("retrieval_agent", "generation_agent")

    # From generation, check if complete
    workflow.add_conditional_edges(
        "generation_agent",
        check_if_complete,
        {
            "supervisor_agent": "supervisor_agent",
            "clarification_agent": "clarification_agent"
        }
    )

    # From supervisor to end
    workflow.add_edge("supervisor_agent", END)

    # From clarification to end
    workflow.add_edge("clarification_agent", END)

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
