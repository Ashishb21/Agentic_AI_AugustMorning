# Multi-Agent Customer Service System with SQL Database

A production-ready example of a multi-agent system using **LangGraph** and **SQLite**, designed for teaching advanced LangChain concepts to students.

## 🎯 Overview

This system demonstrates how multiple specialized AI agents can collaborate through a graph-based workflow to handle different types of customer service queries, accessing a SQL database for real data operations.

### Key Features
- ✅ **6 Specialized Agents** - Classification, Query, Sales, Refund, Analytics, Supervisor
- ✅ **SQL Database Integration** - Real customer, order, product, and refund data
- ✅ **Intelligent Routing** - LLM-based query classification and conditional edges
- ✅ **Production Patterns** - Error handling, validation, escalation
- ✅ **Teaching-Focused** - Clear code organization, extensive comments

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      CUSTOMER QUERY                           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ Classification Agent   │ (Routes to specialist)
                └───────┬────────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────┐
        │               │               │              │
        ▼               ▼               ▼              ▼
    ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
    │ Query  │   │ Sales  │   │ Refund │   │Analytics
    │ Agent  │   │ Agent  │   │ Agent  │   │ Agent
    └──┬─────┘   └──┬─────┘   └──┬─────┘   └──┬─────┘
       │            │            │            │
       └────────────┼────────────┼────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │  SQL Database        │
        │  (customers, orders, │
        │   products, refunds) │
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │ Supervisor Agent     │ (Format response)
        └──────────┬───────────┘
                   │
                   ▼
            ┌────────────┐
            │  RESPONSE  │
            └────────────┘
```

## 📋 File Structure

```
8.Langraph/multi_agent_sql/
├── database_setup.py          # Creates SQLite database & sample data
├── state_schema.py            # TypedDict definition for shared state
├── tools.py                   # SQL query tools (8 different queries)
├── agents.py                  # 6 agent implementations
├── routing.py                 # Conditional edge functions
├── graph.py                   # LangGraph workflow definition
├── main.py                    # Entry point (interactive + demo modes)
├── demo_queries.py            # Test queries and pytest tests
├── README.md                  # This file
├── customer_service.db        # SQLite database (generated)
└── multi_agent_tutorial.ipynb # Interactive Jupyter notebook
```

## 🚀 Quick Start

### 1. Create the Database

```bash
cd 8.Langraph/multi_agent_sql/
python database_setup.py
```

**Output:**
```
Creating database schema...
Inserting sample customers...
Inserting sample products...
Inserting sample orders...
Inserting sample refunds...

Database created successfully at: .../customer_service.db

============================================================
DATABASE SUMMARY
============================================================
Total Customers: 5
Total Products: 10
Total Orders: 15
Orders by Status:
  - pending: 6
  - shipped: 4
  - delivered: 5
  ...
```

### 2. Run Interactive Demo

```bash
python main.py interactive
```

Example interaction:
```
Your query: What's the status of order #1001?

======================================================================
CUSTOMER QUERY: What's the status of order #1001?
======================================================================

[Classification Agent] Analyzing query...
  Classification: order_status (confidence: 0.95)

[Routing] Query type: order_status → query_agent

[Query Agent] Handling order status query...

======================================================================
FINAL RESPONSE
======================================================================

Order #1001 Status Report:
- Product: Laptop Pro
- Quantity: 1
- Total Price: $1299.99
- Status: DELIVERED
- Order Date: 2025-02-04
- Customer: John Doe
- Email: john.doe@email.com

Your order is currently delivered. We'll keep you updated!

---
Is there anything else I can help you with today?
```

### 3. Run Demo Mode

```bash
python main.py demo
```

Runs 5 pre-configured queries demonstrating all agent types.

## 🧠 Agent Specifications

### 1. Classification Agent (Router)
**Role:** Analyze user query and determine query type

**Inputs:** user_query
**Outputs:** query_type, confidence_score, current_agent

**Categories:**
- `order_status` - "Where is my order?", "Status of #1001?"
- `product_info` - "Tell me about laptops", "Do you have phones?"
- `refund` - "I want a refund", "Return order #1002"
- `analytics` - "Sales report", "Top products?"
- `unclear` - Ambiguous or non-service queries

**Implementation:** Uses LLM to classify with confidence scoring

---

### 2. Query Agent (Order Tracking)
**Role:** Handle order status and tracking queries

**Tools:**
- `search_order_by_id(order_id)` - Find order by ID
- `search_order_by_customer_email(email)` - List customer's orders

**Example Flow:**
```
Input: "What's the status of order #1001?"
  ↓
Extract: order_id = 1001
  ↓
SQL: SELECT * FROM orders WHERE order_id = 1001
  ↓
Return: Order details with status
  ↓
Output: Formatted status report
```

---

### 3. Sales Agent (Product Information)
**Role:** Handle product searches and recommendations

**Tools:**
- `search_products(query, category)` - Find products by name/category
- `get_product_details(product_id)` - Get full product info
- `check_stock_availability(product_id, quantity)` - Check stock

**Example Flow:**
```
Input: "Do you have any laptops?"
  ↓
Extract: keyword = "laptop"
  ↓
SQL: SELECT * FROM products WHERE name LIKE '%laptop%'
  ↓
Check: Stock availability for each
  ↓
Output: Product list with prices and stock status
```

---

### 4. Refund Agent (Return Processing)
**Role:** Process refund and return requests

**Tools:**
- `check_refund_eligibility(order_id)` - Validate refund eligibility
- `create_refund_request(order_id, reason, amount)` - Create refund

**Eligibility Rules:**
- ✗ Already refunded
- ✗ Order cancelled
- ✓ All other statuses eligible

**Example Flow:**
```
Input: "I want a refund for order #1002"
  ↓
Extract: order_id = 1002
  ↓
Check: Eligibility
  ↓
If eligible:
  SQL: INSERT INTO refunds (order_id, reason, amount)
  SQL: UPDATE orders SET status = 'refund_requested'
  ↓
Output: Refund confirmation
```

---

### 5. Analytics Agent (Reporting)
**Role:** Generate business reports and insights

**Tools:**
- `get_sales_report()` - Total revenue, order stats
- `get_top_products(limit)` - Top selling products
- `get_customer_stats()` - Customer insights

**Example Flow:**
```
Input: "Show me top selling products"
  ↓
SQL: SELECT * FROM products GROUP BY revenue ORDER BY DESC
  ↓
Format: Top 5 products with revenue and order count
  ↓
Output: Formatted report
```

---

### 6. Supervisor Agent (Final Formatting)
**Role:** Format response and ensure quality

**Input:** Agent response from specialist
**Output:** Final formatted message with closing

---

## 🔄 State Flow

The shared state that flows through all agents:

```python
class CustomerServiceState(TypedDict):
    # Conversation
    messages: List[BaseMessage]
    user_query: str

    # Routing
    query_type: Literal["order_status", "product_info", "refund", "analytics", "unclear"]
    current_agent: str

    # Agent outputs
    sql_query: str
    sql_result: dict
    agent_response: str

    # Control flow
    needs_clarification: bool
    is_complete: bool
    escalate_to_human: bool

    # Context
    customer_id: Optional[str]
    order_id: Optional[str]
    confidence_score: float
```

## 📊 Database Schema

### customers
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### products
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category TEXT
);
```

### orders
```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    total_price REAL,
    status TEXT DEFAULT 'pending',  -- pending, shipped, delivered, cancelled
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### refunds
```sql
CREATE TABLE refunds (
    refund_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pending',  -- pending, approved, rejected
    refund_amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest demo_queries.py -v -s
```

### Run Specific Demo
```bash
python demo_queries.py order         # Order tracking
python demo_queries.py product       # Product search
python demo_queries.py refund        # Refund processing
python demo_queries.py analytics     # Analytics
```

## 💡 Teaching Points

### 1. Multi-Agent Architecture
- Specialized agents with single responsibilities
- Agent collaboration through shared state
- Agent-to-agent routing patterns

### 2. Router Pattern
- Intent classification using LLM
- Confidence scoring
- Dynamic routing based on input

### 3. Conditional Edges
- `route_to_specialist()` - Routes after classification
- `check_if_complete()` - Determines if loop back needed
- Multi-path decision making

### 4. State Management
- Immutable state updates
- State propagation across agents
- Context preservation

### 5. SQL Integration
- Safe parameterized queries
- Database operations in agents
- Tool-based data access

### 6. Real-World Patterns
- Error handling and validation
- Escalation to humans
- Clarification loops
- Response formatting

## 🔧 Customization Guide

### Add a New Agent Type

1. **Add to state_schema.py:**
```python
query_type: Literal[
    "order_status",
    "product_info",
    "refund",
    "new_type",  # Add here
    "analytics",
    "unclear",
]
```

2. **Create agent in agents.py:**
```python
def new_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """New agent implementation"""
    return {
        "agent_response": "...",
        "is_complete": True,
        "current_agent": "new_agent",
    }
```

3. **Update routing.py:**
```python
routing_map = {
    ...
    "new_type": "new_agent",  # Add here
    ...
}
```

4. **Add to graph.py:**
```python
workflow.add_node("new_agent", new_agent)
# Add edges...
```

### Add a New SQL Tool

1. **Implement in tools.py:**
```python
def my_sql_tool(param: str) -> Dict[str, Any]:
    """Tool description"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ... FROM ... WHERE ...", (param,))
    row = cursor.fetchone()
    conn.close()

    return {"found": True, "data": dict(row)}
```

2. **Use in agent:**
```python
result = my_sql_tool("value")
```

## 📚 Learning Resources

- **LangGraph Documentation:** [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **LangChain Documentation:** [python.langchain.com](https://python.langchain.com)
- **SQL Basics:** [sqlitedocs](https://www.sqlite.org/lang.html)
- **Agent Patterns:** See `2-langraph_agents_tutorial.ipynb` in parent directory

## 🚀 Advanced Extensions

1. **Add Memory** - Track conversation history
2. **Human-in-the-Loop** - Approval workflows
3. **Parallel Agents** - Run multiple agents simultaneously
4. **Streaming** - Real-time response streaming
5. **PostgreSQL** - Production database migration
6. **Hybrid Search** - SQL + semantic search
7. **Subgraphs** - Nested agent workflows
8. **Monitoring** - LangSmith integration

## ⚠️ Important Notes

### Database Thread Safety
- SQLite has limitations with concurrent access
- In production, use PostgreSQL or MySQL
- Current implementation is suitable for teaching

### LLM Configuration
- System uses Ollama with `mistral` model
- Ensure Ollama is running: `ollama serve`
- Modify in `agents.py` to use different models

### API Keys
- No API keys required for this demo
- Uses local Ollama instance
- Suitable for offline usage

## 📝 Sample Data

The database is pre-populated with:
- **5 Customers** (John Doe, Jane Smith, Bob Johnson, Alice Williams, Charlie Brown)
- **10 Products** (Laptop Pro, Smartphone X, Headphones, Cable, Stand, Monitor, Keyboard, SSD, Webcam, Phone Case)
- **15 Orders** (various statuses: pending, shipped, delivered, cancelled)
- **3 Refunds** (approved, pending, rejected)

## 🤝 Contributing

To extend this system for your own use case:

1. Fork/copy the directory
2. Modify database schema in `database_setup.py`
3. Add new agents and tools
4. Update routing logic
5. Test with `demo_queries.py`

## 📄 License

This is a teaching resource. Feel free to use and modify for educational purposes.

---

**Last Updated:** March 2026
**Status:** Production-Ready for Teaching
**Tested with:** LangGraph 0.2+, LangChain 0.2+, Python 3.11+
