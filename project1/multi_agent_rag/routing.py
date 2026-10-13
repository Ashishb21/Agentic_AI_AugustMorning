"""
Conditional routing functions for the agentic RAG system.
Determines the flow of the graph based on state conditions.
"""

from typing import Literal

try:
    from state_schema import RAGState
except ImportError:
    from .state_schema import RAGState


def route_after_classification(state: RAGState) -> Literal[
    "retrieval_agent",
    "clarification_agent"
]:
    """
    Routes to the appropriate next agent based on query classification.

    Routes based on query_type:
    - simple/complex → retrieval_agent (process the query)
    - unclear → clarification_agent (request clarification)

    Args:
        state: Current state with query_type

    Returns:
        Name of the next agent node
    """
    query_type = state.get("query_type", "unclear")

    routing_map = {
        "simple": "retrieval_agent",
        "complex": "retrieval_agent",
        "unclear": "clarification_agent"
    }

    agent = routing_map.get(query_type, "clarification_agent")
    print(f"  [Routing] Query type: {query_type} → {agent}")
    return agent


def check_if_complete(state: RAGState) -> Literal[
    "supervisor_agent",
    "clarification_agent"
]:
    """
    Checks if the query has been fully resolved.

    Determines the next step:
    - If complete: route to supervisor for final formatting
    - Otherwise: request clarification or retry

    Args:
        state: Current state with completion flags

    Returns:
        Next node to execute
    """

    # Check if task is complete
    if state.get("is_complete", False):
        print("  [Completion Check] Task complete, routing to supervisor...")
        return "supervisor_agent"

    # Default: unable to process, ask for clarification
    print("  [Completion Check] Unable to process, requesting clarification...")
    return "clarification_agent"
