# Agentic RAG System

A multi-agent retrieval-augmented generation (RAG) system built with LangGraph that demonstrates intelligent query routing, document retrieval, and answer generation.

## Overview

This system combines multiple specialized agents to provide a sophisticated RAG pipeline:

- **Classification Agent**: Analyzes queries and determines complexity level
- **Retrieval Agent**: Intelligently selects and executes search strategies
- **Generation Agent**: Creates comprehensive answers with citations
- **Supervisor Agent**: Formats final responses with proper source attribution
- **Clarification Agent**: Handles ambiguous queries gracefully

The system uses Chroma vector database for document storage and retrieval, and Ollama models for embeddings and generation.

## Architecture

```
START
  ↓
[Classification Agent]
  ↓
[Route based on query type]
  ├─ Simple/Complex → [Retrieval Agent] → [Generation Agent] → [Supervisor] → END
  └─ Unclear → [Clarification Agent] → END
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| State Schema | Defines shared state across agents | TypedDict with comprehensive fields |
| Vector Store | Stores and retrieves documents | Chroma with mxbai-embed-large |
| Tools | Semantic and hybrid search | LangChain @tool decorator |
| Agents | Specialized processing functions | ChatOllama with llama3.2 |
| Graph | Orchestrates agent workflow | LangGraph StateGraph |

## Setup

### Prerequisites

- Python 3.10+
- Ollama with `llama3.2` and `mxbai-embed-large` models
- LangChain and LangGraph libraries

### Installation

1. **Clone and navigate to project**:
   ```bash
   cd /Users/ashishbansal/Documents/Training/AiStack/Aistack_Course/Project_1/8.Langraph/multi_agent_rag
   ```

2. **Install dependencies**:
   ```bash
   pip install langchain langchain-chroma langchain-community langchain-ollama gradio pytest
   ```

3. **Initialize vector store** (one-time setup):
   ```bash
   python vector_store_setup.py
   ```
   This will:
   - Download articles from LangChain and LangGraph documentation
   - Split documents into 1000-character chunks
   - Create embeddings using mxbai-embed-large
   - Store in `chroma_rag_db/` directory

## Usage

### CLI Mode

**Interactive Mode** (default):
```bash
python main.py interactive
```
Commands:
- Enter any question to get an answer
- Type `quit` to exit
- Type `db` to check vector store status

**Single Query**:
```bash
python main.py "What is RAG?"
```

**Demo Mode**:
```bash
python main.py demo
```
Runs pre-defined queries demonstrating different capabilities.

### Web Interface

**Launch Gradio UI**:
```bash
python app.py
```
Then open http://127.0.0.1:7860 in your browser.

Features:
- Clean input/output interface
- Toggle to show/hide retrieved sources
- Display query classification and confidence
- Example questions for quick testing
- JSON view of retrieved documents

### Python API

```python
from main import run_rag_query

# Simple usage
response = run_rag_query("What is retrieval augmented generation?")
print(response)

# With debug info
response = run_rag_query(
    "Compare RAG and fine-tuning",
    debug=True
)
```

## System Workflow

### 1. Classification Phase
- Analyzes query to determine complexity: **simple**, **complex**, or **unclear**
- Uses LLM without tools for speed and efficiency
- Provides confidence score for classification

### 2. Routing Phase
- Simple/Complex queries → proceed to retrieval
- Unclear queries → request clarification and end

### 3. Retrieval Phase
- LLM selects appropriate search method:
  - **Semantic Search**: For conceptual/meaning-based queries
  - **Hybrid Search**: For comprehensive/diverse results
- Executes search against vector store
- Returns top-k documents with relevance scores

### 4. Generation Phase
- Creates prompt with retrieved documents as context
- Generates comprehensive answer with citations
- Extracts citation references from response

### 5. Formatting Phase
- Supervisor agent formats final response
- Adds sources section with document attribution
- Ensures professional presentation

## File Structure

```
multi_agent_rag/
├── __init__.py                      # Package initialization
├── state_schema.py                  # RAGState TypedDict definition
├── vector_store_setup.py            # Chroma setup & document loading
├── tools.py                         # Retrieval tools (semantic/hybrid search)
├── agents.py                        # Agent implementations
├── routing.py                       # Conditional routing functions
├── graph.py                         # LangGraph workflow assembly
├── main.py                          # CLI entry points & execution logic
├── app.py                           # Gradio web interface
├── demo_queries.py                  # Tests and demonstrations
├── README.md                        # This file
└── chroma_rag_db/                   # Vector store (created by setup)
```

## Agents Deep Dive

### Classification Agent
```python
def classification_agent(state: RAGState) -> Dict[str, Any]:
    """
    Analyzes query complexity and confidence.
    Returns: query_type, confidence_score
    """
```
- Prompts LLM to evaluate query type
- Uses JSON parsing for structured output
- No tools required (fast execution)

### Retrieval Agent
```python
def retrieval_agent(state: RAGState) -> Dict[str, Any]:
    """
    Selects and executes search strategy.
    Returns: retrieved_documents, document_scores, retrieval_method
    """
```
- Uses tool calling to select best search method
- Executes semantic or hybrid search
- Handles search failures gracefully

### Generation Agent
```python
def generation_agent(state: RAGState) -> Dict[str, Any]:
    """
    Generates answer with context and citations.
    Returns: generated_answer, citations
    """
```
- Combines retrieved documents with query
- Generates comprehensive answer
- Extracts citations from response

### Supervisor Agent
```python
def supervisor_agent(state: RAGState) -> Dict[str, Any]:
    """
    Formats response with sources.
    Returns: agent_response (final formatted response)
    """
```
- Adds sources section
- Formats citations properly
- Ensures professional presentation

### Clarification Agent
```python
def clarification_agent(state: RAGState) -> Dict[str, Any]:
    """
    Requests clarification for unclear queries.
    Returns: agent_response (clarification request)
    """
```
- Generates helpful clarification request
- Explains why query is unclear
- Suggests how to improve query

## Vector Store

### Ingested Sources

The system comes pre-populated with articles about:
- Retrieval Augmented Generation (RAG)
- Vector databases and embeddings
- LangGraph and LangChain frameworks
- Semantic search techniques
- LLM integration patterns

### Configuration

- **Embedding Model**: `mxbai-embed-large` (via Ollama)
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Collection Name**: `rag_documents`
- **Storage**: Persistent at `./chroma_rag_db/`

### Search Methods

1. **Semantic Search**
   - Similarity-based document retrieval
   - Best for conceptual/meaning-based queries
   - Fast and efficient

2. **Hybrid Search (MMR)**
   - Combines relevance with diversity
   - Prevents redundant results
   - Better for comprehensive coverage

## Testing

### Run Tests
```bash
# All tests
pytest demo_queries.py -v

# Specific test class
pytest demo_queries.py::TestSimpleQueries -v

# With coverage
pytest demo_queries.py --cov=.
```

### Demo Functions
```bash
# All demos
python demo_queries.py

# Specific demos
python demo_queries.py simple    # Simple queries
python demo_queries.py complex   # Complex queries
python demo_queries.py unclear   # Unclear queries
python demo_queries.py test      # Run pytest
```

## Key Concepts

### RAG (Retrieval-Augmented Generation)
Combines document retrieval with LLM generation to:
- Reduce hallucinations
- Ground answers in real documents
- Enable knowledge base Q&A

### Vector Embeddings
Convert text to high-dimensional vectors that capture semantic meaning, enabling similarity-based search.

### LangGraph
Framework for building stateful agent workflows with explicit routing and edge conditions.

### Multi-Agent Orchestration
Specialized agents working together:
- Each agent has a specific responsibility
- Agents communicate via shared state
- Routing determines execution flow

## Configuration

### Model Settings

Edit in `agents.py`:
```python
base_llm = ChatOllama(model="llama3.2", temperature=0.3)
```

### Retrieval Parameters

Edit in `tools.py`:
```python
top_k=5              # Number of documents to retrieve
lambda_mult=0.5      # Diversity vs relevance balance
fetch_k=2*top_k      # Candidates for MMR
```

### Vector Store Parameters

Edit in `vector_store_setup.py`:
```python
chunk_size=1000      # Document chunk size
chunk_overlap=200    # Overlap between chunks
```

## Troubleshooting

### Vector Store Not Found
```bash
python vector_store_setup.py
```

### LLM Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check model availability: `ollama list`

### Poor Search Results
- Check document relevance in `vector_store_setup.py`
- Adjust `top_k` parameter in retrieval tools
- Try different search method (semantic vs hybrid)

### Memory Issues
- Reduce `chunk_size` in vector store setup
- Lower `top_k` in retrieval tools
- Use smaller models (if available)

## Performance

Typical query execution times:
- **Classification**: ~1-2 seconds
- **Retrieval**: ~1-2 seconds
- **Generation**: ~3-5 seconds
- **Total**: ~5-9 seconds

Factors affecting performance:
- LLM response time
- Document retrieval complexity
- Generated answer length

## Future Enhancements

Potential improvements:
- [ ] Streaming responses for long answers
- [ ] Multi-turn conversation support
- [ ] Document ranking with cross-encoders
- [ ] Query expansion and decomposition
- [ ] Answer validation and fact-checking
- [ ] Custom knowledge base upload
- [ ] Response caching for repeated queries
- [ ] A/B testing for retrieval strategies

## Project Structure Comparison

This RAG system follows the same architectural patterns as the `multi_agent_sql` project:

| Component | multi_agent_sql | multi_agent_rag |
|-----------|-----------------|-----------------|
| State | CustomerServiceState | RAGState |
| Tools | SQL query tools | Search tools |
| Agents | Query/Sales/Refund/Analytics | Classification/Retrieval/Generation |
| Graph | StateGraph with routing | StateGraph with routing |
| Entry | CLI + Interactive | CLI + Gradio UI |
| Testing | Pytest + demos | Pytest + demos |

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Chroma Vector Database](https://www.trychroma.com/)
- [Ollama Models](https://ollama.ai/)

## License

Educational project - Part of AiStack course curriculum

---

**Created**: March 2026
**Framework**: LangGraph + LangChain
**LLM**: Ollama (llama3.2)
**Embeddings**: mxbai-embed-large
