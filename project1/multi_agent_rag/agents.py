"""
Agent implementations for the agentic RAG system.
Each agent handles a specific role in the retrieval-augmented generation pipeline.
"""

import re
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama

try:
    from state_schema import RAGState
    from tools import (
        RETRIEVAL_TOOLS,
        semantic_search,
        hybrid_search,
    )
except ImportError:
    from .state_schema import RAGState
    from .tools import (
        RETRIEVAL_TOOLS,
        semantic_search,
        hybrid_search,
    )


# ==================== SPECIALIZED LLM INSTANCES ====================

# Base LLM for classification and clarification (no tools bound)
base_llm = ChatOllama(model="llama3.2", temperature=0.3)

# LLM with retrieval tools bound for intelligent tool selection
retrieval_llm = base_llm.bind_tools(RETRIEVAL_TOOLS)


# ==================== HELPER FUNCTIONS ====================

def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """
    Execute a retrieval tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Dictionary of arguments to pass to the tool

    Returns:
        Dictionary with tool execution result
    """
    tool_map = {
        "semantic_search": semantic_search,
        "hybrid_search": hybrid_search,
    }

    tool_obj = tool_map.get(tool_name)
    if not tool_obj:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        # Type conversion for common patterns
        converted_args = {}
        for key, value in tool_args.items():
            if key == "top_k" and isinstance(value, str):
                try:
                    converted_args[key] = int(value)
                except (ValueError, AttributeError):
                    converted_args[key] = value
            else:
                converted_args[key] = value

        # Execute the tool
        if hasattr(tool_obj, 'func'):
            result = tool_obj.func(**converted_args)
        else:
            result = tool_obj(**converted_args)
        return result
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


# ==================== CLASSIFICATION AGENT ====================

def classification_agent(state: RAGState) -> Dict[str, Any]:
    """
    Analyzes the user query and classifies it into one of 3 categories.

    Categories:
    - simple: Factual questions with direct answers (e.g., "What is RAG?")
    - complex: Comparison or reasoning questions (e.g., "Compare A and B")
    - unclear: Ambiguous or insufficient information

    Args:
        state: Current conversation state

    Returns:
        Updated state with query classification
    """
    print("\n[Classification Agent] Analyzing query...")

    query = state["user_query"]

    # Create classification prompt
    classification_prompt = f"""You are a query classifier for a RAG system. Analyze the customer query and classify it into ONE of these categories:

1. simple - Factual questions with straightforward answers (e.g., "What is X?", "Explain Y")
2. complex - Comparison, reasoning, or multi-part questions (e.g., "Compare X and Y", "Why does X work?")
3. unclear - Ambiguous, vague, or insufficient information

Customer Query: "{query}"

Respond in JSON format ONLY:
{{
    "query_type": "<one of: simple, complex, unclear>",
    "confidence_score": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
}}"""

    # Get classification from LLM
    messages = [HumanMessage(content=classification_prompt)]
    response = base_llm.invoke(messages)

    # Parse response
    try:
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            classification = json.loads(json_match.group())
        else:
            classification = {
                "query_type": "unclear",
                "confidence_score": 0.0,
                "reasoning": "Could not parse response"
            }
    except:
        classification = {
            "query_type": "unclear",
            "confidence_score": 0.0,
            "reasoning": "JSON parsing failed"
        }

    query_type = classification.get("query_type", "unclear")
    confidence = classification.get("confidence_score", 0.0)

    print(f"  Classification: {query_type} (confidence: {confidence:.2f})")

    return {
        "query_type": query_type,
        "current_agent": "classification_agent",
        "confidence_score": confidence,
    }


# ==================== RETRIEVAL AGENT ====================

def retrieval_agent(state: RAGState) -> Dict[str, Any]:
    """
    Selects and executes the appropriate retrieval tool.

    Uses the LLM with tool calling to intelligently choose between
    semantic_search and hybrid_search based on query characteristics.

    Args:
        state: Current state with user_query

    Returns:
        Updated state with retrieved documents
    """
    print("\n[Retrieval Agent] Searching for relevant documents...")

    query = state["user_query"]
    messages = list(state.get("messages", []))

    # Add retrieval task
    retrieval_prompt = f"""You are a document retrieval expert. Given the query, select the most appropriate search method:

Query: "{query}"

Use semantic_search for conceptual/meaning-based queries.
Use hybrid_search for queries that need diverse results or comparisons.

Select the best tool and execute it."""

    messages.append(HumanMessage(content=retrieval_prompt))

    # Get tool choice from LLM
    response = retrieval_llm.invoke(messages)

    # Check if tool calls were made
    retrieved_documents = []
    document_scores = []
    retrieval_method = "semantic"

    if response.tool_calls:
        # Execute the selected tool
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})

            print(f"  Selected: {tool_name}")
            result = execute_tool(tool_name, tool_args)

            if result.get("found"):
                retrieved_documents = result.get("documents", [])
                document_scores = result.get("scores", [])
                retrieval_method = result.get("method", tool_name)

                print(f"  Found {len(retrieved_documents)} documents")
            else:
                print(f"  No documents found: {result.get('error', result.get('message', ''))}")

            # Add tool message to messages
            messages.append(AIMessage(content=response.content, tool_calls=response.tool_calls))
            messages.append(ToolMessage(
                content=json.dumps(result),
                tool_call_id=tool_call["id"]
            ))

    if not retrieved_documents:
        print("  WARNING: No documents retrieved, using empty results")

    return {
        "messages": messages,
        "retrieved_documents": retrieved_documents,
        "document_scores": document_scores,
        "retrieval_method": retrieval_method,
        "current_agent": "retrieval_agent",
    }


# ==================== GENERATION AGENT ====================

def generation_agent(state: RAGState) -> Dict[str, Any]:
    """
    Generates an answer using retrieved documents as context.

    Creates a prompt that includes relevant documents and uses the LLM
    to generate a comprehensive answer with citations.

    Args:
        state: Current state with retrieved_documents

    Returns:
        Updated state with generated_answer and citations
    """
    print("\n[Generation Agent] Generating answer...")

    query = state["user_query"]
    documents = state.get("retrieved_documents", [])

    # Format documents for context
    context_text = ""
    if documents:
        context_text = "Retrieved documents:\n\n"
        for i, doc in enumerate(documents, 1):
            source = doc.get("source", "Unknown")
            content = doc.get("content", "")[:300]  # Truncate for readability
            context_text += f"[{i}] Source: {source}\n{content}...\n\n"
    else:
        context_text = "No documents were retrieved for this query.\n\n"

    # Create generation prompt
    generation_prompt = f"""Based on the following retrieved documents, answer the user's query.
If documents are available, cite them using [1], [2], etc. references.
If no documents are available, provide your best knowledge-based answer.

{context_text}

User Query: "{query}"

Provide a clear, informative answer:"""

    messages = [HumanMessage(content=generation_prompt)]
    response = base_llm.invoke(messages)
    generated_answer = response.content

    # Extract citations from the answer
    citations = []
    citation_pattern = r'\[(\d+)\]'
    matches = re.findall(citation_pattern, generated_answer)

    if matches:
        citation_indices = sorted(set(int(m) for m in matches))
        for idx in citation_indices:
            if 0 < idx <= len(documents):
                doc = documents[idx - 1]
                citations.append({
                    "index": idx,
                    "source": doc.get("source", "Unknown"),
                    "excerpt": doc.get("content", "")[:200]
                })

    print(f"  Generated answer with {len(citations)} citations")

    return {
        "generated_answer": generated_answer,
        "citations": citations,
        "is_complete": True,
        "current_agent": "generation_agent",
    }


# ==================== SUPERVISOR AGENT ====================

def supervisor_agent(state: RAGState) -> Dict[str, Any]:
    """
    Formats the final response with sources and citations.

    Combines the generated answer with properly formatted citations
    and source information.

    Args:
        state: Current state with generated_answer and citations

    Returns:
        Updated state with agent_response (final formatted response)
    """
    print("\n[Supervisor Agent] Formatting final response...")

    answer = state.get("generated_answer", "")
    citations = state.get("citations", [])
    documents = state.get("retrieved_documents", [])

    # Format response
    final_response = f"{answer}\n\n"

    # Add sources section
    if citations or documents:
        final_response += "=" * 50 + "\nSOURCES\n" + "=" * 50 + "\n"

        if citations:
            for cite in citations:
                idx = cite.get("index", "?")
                source = cite.get("source", "Unknown")
                final_response += f"[{idx}] {source}\n"
        else:
            # Add document sources if no citations were extracted
            for i, doc in enumerate(documents[:3], 1):
                source = doc.get("source", "Unknown")
                final_response += f"[{i}] {source}\n"

    return {
        "agent_response": final_response,
        "current_agent": "supervisor_agent",
    }


# ==================== CLARIFICATION AGENT ====================

def clarification_agent(state: RAGState) -> Dict[str, Any]:
    """
    Handles unclear queries by requesting clarification.

    When a query cannot be classified or processed, this agent
    generates a helpful clarification request.

    Args:
        state: Current state with user_query

    Returns:
        Updated state with clarification request
    """
    print("\n[Clarification Agent] Requesting clarification...")

    query = state["user_query"]

    # Create clarification prompt
    clarification_prompt = f"""The user's query is unclear or ambiguous. Generate a helpful response that:
1. Acknowledges what they asked
2. Explains why it's unclear
3. Asks for clarification with specific suggestions

User Query: "{query}"

Generate a natural, helpful clarification request:"""

    messages = [HumanMessage(content=clarification_prompt)]
    response = base_llm.invoke(messages)
    clarification_text = response.content

    clarification_response = f"""I'd like to help, but I need a bit more information:

{clarification_text}

Please provide more details so I can better assist you."""

    return {
        "agent_response": clarification_response,
        "needs_clarification": True,
        "is_complete": True,
        "current_agent": "clarification_agent",
    }
