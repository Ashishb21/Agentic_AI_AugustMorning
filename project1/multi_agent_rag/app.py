"""
Gradio web interface for the agentic RAG system.
Provides a user-friendly UI for interacting with the RAG pipeline.
"""

import json
from pathlib import Path

import gradio as gr

try:
    from main import run_rag_query, get_initial_state
    from graph import create_graph
    from vector_store_setup import get_vector_store
except ImportError:
    from .main import run_rag_query, get_initial_state
    from .graph import create_graph
    from .vector_store_setup import get_vector_store


def rag_interface(query: str, show_sources: bool = True) -> tuple:
    """
    Process query through RAG system and return formatted response.

    Args:
        query: User's question
        show_sources: Whether to display retrieved sources

    Returns:
        Tuple of (response, query_type, confidence, sources_json)
    """
    # Check vector store
    vector_store_path = Path(__file__).parent / "chroma_rag_db"
    if not vector_store_path.exists():
        return (
            "Error: Vector store not found. Please run vector_store_setup.py first.",
            "N/A",
            0.0,
            {}
        )

    try:
        # Create graph and run query
        app = create_graph()
        initial_state = get_initial_state(query)

        # Suppress agent print statements during web execution
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        final_state = app.invoke(initial_state)

        sys.stdout = old_stdout

        # Extract components
        response = final_state.get("agent_response", "No response generated")
        query_type = final_state.get("query_type", "N/A")
        confidence = final_state.get("confidence_score", 0.0)

        # Prepare sources
        sources = {}
        if show_sources:
            documents = final_state.get("retrieved_documents", [])
            for i, doc in enumerate(documents, 1):
                sources[f"Source {i}"] = {
                    "title": doc.get("source", "Unknown"),
                    "excerpt": doc.get("content", "")[:300]
                }

        return (
            response,
            query_type,
            confidence,
            sources
        )

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return (
            f"Error processing query: {str(e)}\n\n{error_detail}",
            "error",
            0.0,
            {}
        )


def create_ui():
    """
    Create and return the Gradio interface.

    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(title="Agentic RAG System", theme=gr.themes.Soft()) as demo:

        gr.Markdown("# 🤖 Agentic RAG System")
        gr.Markdown(
            "Multi-agent retrieval-augmented generation powered by LangGraph\n\n"
            "Ask questions about AI, LangGraph, RAG, and related topics."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask me anything about AI, LangGraph, or RAG...",
                    lines=3,
                    show_copy_button=False
                )
                show_sources = gr.Checkbox(
                    label="Show Retrieved Sources",
                    value=True
                )
                submit_btn = gr.Button("Submit", variant="primary", size="lg")

            with gr.Column():
                gr.Markdown("### Response")
                answer_output = gr.Textbox(
                    label="Answer",
                    lines=10,
                    show_copy_button=True,
                    interactive=False
                )

        with gr.Row():
            with gr.Column():
                query_type_output = gr.Textbox(
                    label="Query Type",
                    interactive=False
                )
            with gr.Column():
                confidence_output = gr.Number(
                    label="Confidence Score",
                    interactive=False,
                    precision=2
                )

        gr.Markdown("### Retrieved Sources")
        sources_output = gr.JSON(
            label="Documents Retrieved",
            interactive=False
        )

        # Examples
        gr.Examples(
            examples=[
                "What is retrieval augmented generation?",
                "How does semantic search work?",
                "Compare vector embeddings and keyword search",
                "What are the benefits of using vector databases?",
                "Explain how LangGraph enables multi-agent systems",
            ],
            inputs=query_input,
            label="Try these example questions"
        )

        # Connect button
        submit_btn.click(
            fn=rag_interface,
            inputs=[query_input, show_sources],
            outputs=[answer_output, query_type_output, confidence_output, sources_output]
        )

        # Allow Enter key to submit
        query_input.submit(
            fn=rag_interface,
            inputs=[query_input, show_sources],
            outputs=[answer_output, query_type_output, confidence_output, sources_output]
        )

        # Footer
        gr.Markdown(
            "---\n"
            "**System Info:**\n"
            "- Classification Agent: Analyzes query complexity\n"
            "- Retrieval Agent: Searches vector store for relevant documents\n"
            "- Generation Agent: Creates answer with citations\n"
            "- Supervisor Agent: Formats final response with sources"
        )

    return demo


if __name__ == "__main__":
    # Check vector store before launching
    vector_store_path = Path(__file__).parent / "chroma_rag_db"

    if not vector_store_path.exists():
        print("Vector store not found. Attempting to set it up...")
        try:
            from vector_store_setup import setup_vector_store
            setup_vector_store()
            print("Vector store setup complete!")
        except Exception as e:
            print(f"Vector store setup failed: {str(e)}")
            print("Please run: python vector_store_setup.py")

    # Create and launch UI
    app = create_ui()
    app.launch(share=False, server_name="127.0.0.1", server_port=7860)
