"""
State schema for the multi-agent customer service system.
Defines the shared state that flows through all agents in the graph.
"""

from typing import TypedDict, List, Literal, Optional
from langchain_core.messages import BaseMessage


class CustomerServiceState(TypedDict):
    """
    Shared state that flows through all agents in the multi-agent system.

    Attributes:
        messages: List of BaseMessage objects (conversation history)
        user_query: The original user query
        query_type: Classification of the query intent
        current_agent: Name of the agent that just processed
        sql_query: The SQL query executed
        sql_result: The result from the database query
        agent_response: The agent's textual response
        needs_clarification: Whether the agent needs clarification
        is_complete: Whether the query has been fully resolved
        escalate_to_human: Whether to escalate to a human agent
        customer_id: Extracted customer ID from query (if applicable)
        order_id: Extracted order ID from query (if applicable)
        confidence_score: Confidence in the classification (0-1)
    """

    messages: List[BaseMessage]
    user_query: str
    query_type: Literal[
        "order_status",
        "product_info",
        "refund",
        "analytics",
        "unclear",
    ]
    current_agent: str
    sql_query: str
    sql_result: dict
    agent_response: str
    needs_clarification: bool
    is_complete: bool
    escalate_to_human: bool
    customer_id: Optional[str]
    order_id: Optional[str]
    confidence_score: float
