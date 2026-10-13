"""
State schema for the agentic RAG system.
Defines the shared state that flows through all agents in the graph.
"""

from typing import TypedDict, List, Literal, Optional, Any
from langchain_core.messages import BaseMessage


class RAGState(TypedDict):
    """
    Shared state that flows through all agents in the multi-agent RAG system.

    Attributes:
        messages: List of BaseMessage objects (conversation history)
        user_query: The original user query
        query_type: Classification of the query (simple, complex, unclear)
        current_agent: Name of the agent that just processed
        retrieved_documents: List of retrieved document chunks with metadata
        document_scores: Relevance scores for retrieved documents
        retrieval_method: Method used for retrieval (semantic or hybrid)
        generated_answer: The LLM-generated answer
        citations: List of source documents used in the answer
        confidence_score: Confidence in the classification and answer (0-1)
        is_complete: Whether the query has been fully resolved
        needs_clarification: Whether clarification is needed from the user
        agent_response: The final formatted response to the user
        tool_calls: LLM's tool call requests from agent
        tool_results: Results from tool execution
    """

    messages: List[BaseMessage]
    user_query: str
    query_type: Literal["simple", "complex", "unclear"]
    current_agent: str
    retrieved_documents: List[dict]
    document_scores: List[float]
    retrieval_method: str
    generated_answer: str
    citations: List[str]
    confidence_score: float
    is_complete: bool
    needs_clarification: bool
    agent_response: str
    tool_calls: Optional[List[dict]]
    tool_results: Optional[List[dict]]
