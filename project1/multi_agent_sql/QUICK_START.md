# Multi-Agent System - Quick Start Guide

## 🚀 Get Running in 2 Minutes

### 1. Ensure Database Exists
```bash
cd /Users/ashishbansal/Documents/Training/AiStack/Aistack_Course/Project_1/8.Langraph/multi_agent_sql
ls customer_service.db  # Should exist
```

### 2. Run Interactive Mode
```bash
python main.py interactive
```

### 3. Try These Queries
```
Your query: What's the status of order #1001?
Your query: Do you have any laptops?
Your query: I want a refund for order #1002
Your query: Show me your top selling products
Your query: quit
```

---

## 📚 Understanding the System in 5 Minutes

### The Flow
```
1. User Query
   ↓
2. Classification Agent (determines intent)
   ↓
3. Router (picks the right agent)
   ↓
4. Specialist Agent (handles the request)
   - Query Agent (orders)
   - Sales Agent (products)
   - Refund Agent (returns)
   - Analytics Agent (reports)
   ↓
5. Database Query (gets the data)
   ↓
6. Supervisor Agent (formats response)
   ↓
7. User Response
```

### 5 Key Concepts

| Concept | What It Does | Example |
|---------|-------------|---------|
| **Classification** | Understands user intent | "What's my order?" → order_status |
| **Routing** | Sends to right agent | order_status → Query Agent |
| **Agents** | Specialized handlers | Query Agent searches orders table |
| **Tools** | Database queries | search_order_by_id(1001) |
| **State** | Shared data across system | query_type, sql_result, response |

---

## 🧪 Run Different Demo Modes

### Demo Mode (Pre-configured Queries)
```bash
python main.py demo
```

### Test Specific Agents
```bash
python demo_queries.py order        # Order tracking tests
python demo_queries.py product      # Product search tests
python demo_queries.py refund       # Refund processing tests
python demo_queries.py analytics    # Analytics tests
```

### Run All Unit Tests
```bash
pytest demo_queries.py -v -s
```

---

## 📁 Key Files Explained

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `agents.py` | 6 specialized agents | classification_agent, query_agent, sales_agent, etc. |
| `tools.py` | SQL database queries | search_order_by_id, search_products, get_sales_report |
| `routing.py` | Decision logic | route_to_specialist, check_if_complete |
| `graph.py` | LangGraph workflow | create_graph(), visualize_graph() |
| `state_schema.py` | Shared state | CustomerServiceState TypedDict |
| `main.py` | Entry point | run_customer_service(), get_initial_state() |

---

## 🎯 What Each Agent Does

### 1. Classification Agent
- **Role**: Understands user intent
- **Input**: User query
- **Output**: Query type (order_status, product_info, refund, analytics, unclear)
- **Example**: "What's my order?" → "order_status"

### 2. Query Agent
- **Role**: Tracks orders
- **Tools**: search_order_by_id, search_order_by_customer_email
- **Input**: Order ID or email
- **Output**: Order details and status
- **Example**: Order #1001 is "delivered"

### 3. Sales Agent
- **Role**: Provides product information
- **Tools**: search_products, check_stock_availability
- **Input**: Product name or keyword
- **Output**: Product list with prices and stock
- **Example**: Laptops in stock: Laptop Pro ($1299.99)

### 4. Refund Agent
- **Role**: Processes refunds
- **Tools**: check_refund_eligibility, create_refund_request
- **Input**: Order ID and reason
- **Output**: Refund confirmation
- **Example**: Refund approved for $1299.99

### 5. Analytics Agent
- **Role**: Generates reports
- **Tools**: get_sales_report, get_top_products, get_customer_stats
- **Input**: Report request
- **Output**: Business metrics
- **Example**: Top 5 products by revenue

### 6. Supervisor Agent
- **Role**: Formats final response
- **Input**: Agent response
- **Output**: Polished message with closing
- **Example**: Adds "Is there anything else?"

---

## 💾 Database Tables

### customers
```sql
customer_id | name         | email                  | phone
1           | John Doe     | john.doe@email.com     | 555-0101
2           | Jane Smith   | jane.smith@email.com   | 555-0102
...
```

### products
```sql
product_id | name              | price  | stock_quantity | category
1          | Laptop Pro        | 1299.99| 15            | Electronics
2          | Smartphone X      | 899.99 | 25            | Electronics
...
```

### orders
```sql
order_id | customer_id | product_id | quantity | total_price | status    | order_date
1001     | 1           | 1          | 1        | 1299.99     | delivered | 2025-02-04
1002     | 2           | 3          | 1        | 199.99      | shipped   | 2025-02-20
...
```

### refunds
```sql
refund_id | order_id | reason                    | status  | refund_amount
1         | 12       | Product doesn't work      | approved| 1299.99
2         | 4        | Changed my mind           | pending | 39.98
...
```

---

## 🔍 Example Interactions

### Example 1: Order Status Query
```
User: "What's the status of order #1001?"

1. Classification Agent → "order_status" (confidence: 95%)
2. Router → sends to Query Agent
3. Query Agent → extracts order_id=1001
4. Database → SELECT * FROM orders WHERE order_id=1001
5. Response → "Order #1001: Laptop Pro - DELIVERED"
6. Supervisor → formats with closing message
```

### Example 2: Product Search
```
User: "Do you have any laptops?"

1. Classification Agent → "product_info" (confidence: 98%)
2. Router → sends to Sales Agent
3. Sales Agent → extracts keyword="laptop"
4. Database → SELECT * FROM products WHERE name LIKE '%laptop%'
5. Response → "Found 1 product: Laptop Pro - $1299.99 (15 in stock)"
6. Supervisor → adds closing message
```

### Example 3: Refund Request
```
User: "I want a refund for order #1002"

1. Classification Agent → "refund" (confidence: 99%)
2. Router → sends to Refund Agent
3. Refund Agent → extracts order_id=1002
4. Check Eligibility → is order #1002 eligible?
5. Create Refund → INSERT INTO refunds (...) and UPDATE orders
6. Response → "Refund approved for $199.99 (pending)"
7. Supervisor → formats professional message
```

---

## 🎓 Learning Path

### Beginner
1. Run `python main.py interactive`
2. Try different types of queries
3. Read the output messages
4. Look at `README.md`

### Intermediate
1. Run `python main.py demo`
2. Read `agents.py` - understand each agent
3. Read `tools.py` - understand SQL queries
4. Read `routing.py` - understand logic flow

### Advanced
1. Open `multi_agent_sql_tutorial.ipynb` in Jupyter
2. Run each cell and see intermediate results
3. Study `graph.py` - understand LangGraph structure
4. Modify code and add your own agents

---

## 🛠️ Common Tasks

### See SQL Being Executed
```python
# In agents.py, look for print statements
# Each agent prints what it's doing
# Run with: python main.py "Your query"
```

### Add a New Product Search Term
Edit `sales_agent()` in `agents.py`:
```python
keywords = ["laptop", "phone", "headphone", "cable", "stand",
            "monitor", "keyboard", "ssd", "webcam", "case",
            "NEW_KEYWORD"]  # Add here
```

### Change LLM Model
Edit `agents.py`:
```python
llm = ChatOllama(model="neural-chat", temperature=0.3)  # Change "mistral"
```

### Add New Order Status
Edit database_setup.py and re-run:
```bash
python database_setup.py
```

---

## ❓ Troubleshooting

### "Database not found" Error
```bash
cd /Users/ashishbansal/Documents/Training/AiStack/Aistack_Course/Project_1/8.Langraph/multi_agent_sql
python database_setup.py
```

### "Ollama connection error"
```bash
# Make sure Ollama is running
ollama serve

# In another terminal
python main.py interactive
```

### "ImportError" when running script
```bash
# Make sure you're in the right directory
cd /Users/ashishbansal/Documents/Training/AiStack/Aistack_Course/Project_1/8.Langraph/multi_agent_sql
python main.py interactive
```

### Queries returning no results
Check that:
1. Database exists: `ls customer_service.db`
2. Sample data loaded: Run `python database_setup.py` again
3. Query format is correct: Try `What's the status of order #1001?`

---

## 📖 Further Reading

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `IMPLEMENTATION_GUIDE.md`
- **Interactive Tutorial**: See `multi_agent_sql_tutorial.ipynb`
- **LangGraph Docs**: https://github.com/langchain-ai/langgraph
- **LangChain Docs**: https://python.langchain.com

---

## 🎯 What to Try Next

1. ✅ Run interactive mode with 3-5 queries
2. ✅ Run demo mode to see all agents
3. ✅ Read README.md for agent details
4. ✅ Open Jupyter notebook for interactive learning
5. ✅ Modify a query tool to add new functionality
6. ✅ Create your own test case in demo_queries.py
7. ✅ Add a new agent type (e.g., Shipping Agent)

---

**Total Time to Understand System: 15-30 minutes**
**Total Time to Master System: 2-4 hours**
**Total Time to Extend System: 2-4 hours per new feature**

Good luck! 🚀
