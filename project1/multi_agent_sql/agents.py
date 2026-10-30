"""
Agent implementations for the multi-agent customer service system.
Each agent handles a specific type of customer query.
"""

import re
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

try:
    from state_schema import CustomerServiceState
    from tools import (
        search_order_by_id,
        search_order_by_customer_email,
        search_products,
        get_product_details,
        check_stock_availability,
        check_refund_eligibility,
        create_refund_request,
        get_sales_report,
        get_top_products,
        get_customer_stats,
    )
except ImportError:
    from .state_schema import CustomerServiceState
    from .tools import (
        search_order_by_id,
        search_order_by_customer_email,
        search_products,
        get_product_details,
        check_stock_availability,
        check_refund_eligibility,
        create_refund_request,
        get_sales_report,
        get_top_products,
        get_customer_stats,
    )

# Initialize LLM (using Ollama)
llm = ChatOllama(model="llama3.2", temperature=0.3)


# ==================== CLASSIFICATION AGENT ====================

def classification_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Analyzes the user query and classifies it into one of 5 categories.

    Categories:
    - order_status: Check order status, tracking, delivery info
    - product_info: Product details, recommendations, availability
    - refund: Process refund or return requests
    - analytics: Reports, statistics, business insights
    - unclear: Ambiguous or unclear intent

    Args:
        state: Current conversation state

    Returns:
        Updated state with query classification
    """
    print("\n[Classification Agent] Analyzing query...")

    query = state["user_query"]

    # Create classification prompt
    classification_prompt = f"""You are a customer service query classifier. Analyze the customer query and classify it into ONE of these categories:

1. order_status - Questions about order tracking, delivery status, shipping info
2. product_info - Questions about products, prices, recommendations, availability
3. refund - Requests for refunds, returns, cancellations
4. analytics - Requests for reports, statistics, business insights (only for internal use)
5. unclear - Ambiguous, non-service queries, or anything that doesn't fit above

Customer Query: "{query}"

Respond in JSON format ONLY:
{{
    "query_type": "<one of: order_status, product_info, refund, analytics, unclear>",
    "confidence_score": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
}}"""

    # Get classification from LLM
    messages = [HumanMessage(content=classification_prompt)]
    response = llm.invoke(messages)

    # Parse response
    try:
        # Extract JSON from response
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
        "is_complete": False,
        "needs_clarification": confidence < 0.6,
        "escalate_to_human": False,
    }


# ==================== QUERY AGENT ====================

def query_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Handles order status queries.
    Searches for orders and provides status information.

    Args:
        state: Current conversation state

    Returns:
        Updated state with order information
    """
    print("\n[Query Agent] Handling order status query...")

    query = state["user_query"]

    # Try to extract order ID from query
    order_match = re.search(r'#?(\d+)', query)
    refund_match = re.search(r'order\s+#?(\d+)', query, re.IGNORECASE)

    order_id = None
    if refund_match:
        order_id = int(refund_match.group(1))
    elif order_match:
        order_id = int(order_match.group(1))

    result = {"current_agent": "query_agent"}

    if order_id:
        # Search by order ID
        order_result = search_order_by_id(order_id)

        if order_result.get("found"):
            order = order_result["order"]
            response = f"""Order #{order['order_id']} Status Report:
- Product: {order['product_name']}
- Quantity: {order['quantity']}
- Total Price: ${order['total_price']:.2f}
- Status: {order['status'].upper()}
- Order Date: {order['order_date']}
- Customer: {order['customer_name']}
- Email: {order['email']}

Your order is currently {order['status']}. We'll keep you updated!"""

            result.update({
                "agent_response": response,
                "sql_result": order_result,
                "is_complete": True,
                "needs_clarification": False,
            })
        else:
            result.update({
                "agent_response": f"I couldn't find order #{order_id}. Could you provide another order number?\n\nNote: Valid order IDs are numbers 1-15 (e.g., #1, #5, #10).",
                "is_complete": True,
                "needs_clarification": False,
            })
    else:
        # Try to extract email and search
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)

        if email_match:
            email = email_match.group(0)
            orders_result = search_order_by_customer_email(email)

            if orders_result.get("found"):
                orders = orders_result["orders"]
                response = f"Found {len(orders)} order(s) for {email}:\n\n"

                for order in orders:
                    response += f"• Order #{order['order_id']}: {order['product_name']} - {order['status'].upper()}\n"

                result.update({
                    "agent_response": response,
                    "sql_result": orders_result,
                    "is_complete": True,
                    "needs_clarification": False,
                })
            else:
                result.update({
                    "agent_response": f"No orders found for {email}. This email doesn't have any order history.",
                    "is_complete": True,
                    "needs_clarification": False,
                })
        else:
            result.update({
                "agent_response": "I need more information to look up your order. Please provide:\n- An order number (e.g., #1, #5, #10)\n- Or your email address\n\nFor example: 'What's the status of order #5?' or 'My email is john.doe@email.com'",
                "is_complete": True,
                "needs_clarification": False,
            })

    return result


# ==================== SALES AGENT ====================

def sales_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Handles product information queries.
    Searches for products and provides details.

    Args:
        state: Current conversation state

    Returns:
        Updated state with product information
    """
    print("\n[Sales Agent] Handling product information query...")

    query = state["user_query"]

    # Extract product keywords
    keywords = ["laptop", "phone", "headphone", "cable", "stand", "monitor", "keyboard", "ssd", "webcam", "case"]
    found_keyword = None

    for keyword in keywords:
        if keyword in query.lower():
            found_keyword = keyword
            break

    if found_keyword:
        # Search for products
        search_result = search_products(found_keyword)

        if search_result.get("found"):
            products = search_result["products"]
            response = f"Found {len(products)} matching product(s):\n\n"

            for product in products:
                stock_status = "In Stock" if product["stock_quantity"] > 0 else "Out of Stock"
                response += f"• {product['name']}\n"
                response += f"  Price: ${product['price']:.2f}\n"
                response += f"  Category: {product['category']}\n"
                response += f"  Stock: {product['stock_quantity']} units ({stock_status})\n"
                response += f"  Description: {product['description']}\n\n"

            return {
                "agent_response": response,
                "sql_result": search_result,
                "is_complete": True,
                "needs_clarification": False,
                "current_agent": "sales_agent",
            }
        else:
            return {
                "agent_response": f"I couldn't find any {found_keyword} products in our catalog. We have:\n- Laptops\n- Smartphones\n- Headphones\n- Keyboards\n- Monitors\n- SSDs\n\nWould you like to search for any of these?",
                "is_complete": True,
                "needs_clarification": False,
                "current_agent": "sales_agent",
            }
    else:
        # Use LLM to understand product query
        extraction_prompt = f"""Extract the product or category the customer is asking about from this query: "{query}"
Respond with just the product name or category (2-3 words max)."""

        messages = [HumanMessage(content=extraction_prompt)]
        product_extraction = llm.invoke(messages)
        product_query = product_extraction.content.strip()

        search_result = search_products(product_query)

        if search_result.get("found"):
            products = search_result["products"]
            response = f"Products related to '{product_query}':\n\n"

            for product in products:
                stock_status = "In Stock" if product["stock_quantity"] > 0 else "Out of Stock"
                response += f"• {product['name']} - ${product['price']:.2f} ({stock_status})\n"

            return {
                "agent_response": response,
                "sql_result": search_result,
                "is_complete": True,
                "needs_clarification": False,
                "current_agent": "sales_agent",
            }
        else:
            return {
                "agent_response": "I couldn't find the product you're looking for. Could you describe it more specifically? We carry electronics, peripherals, and accessories.",
                "is_complete": True,
                "needs_clarification": False,
                "current_agent": "sales_agent",
            }


# ==================== REFUND AGENT ====================

def refund_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Handles refund requests.
    Checks eligibility and processes refunds.

    Args:
        state: Current conversation state

    Returns:
        Updated state with refund status
    """
    print("\n[Refund Agent] Processing refund request...")

    query = state["user_query"]

    # Extract order ID
    order_match = re.search(r'#?(\d+)', query)

    if not order_match:
        return {
            "agent_response": "To process a refund, please provide your order number (e.g., #1, #5, #10). Valid orders are numbered 1-15.",
            "is_complete": True,
            "needs_clarification": False,
            "current_agent": "refund_agent",
        }

    order_id = int(order_match.group(1))

    # Check eligibility
    eligibility = check_refund_eligibility(order_id)

    if not eligibility.get("eligible"):
        return {
            "agent_response": f"Unfortunately, order #{order_id} is not eligible for refund. Reason: {eligibility.get('reason')}",
            "is_complete": True,
            "needs_clarification": False,
            "current_agent": "refund_agent",
        }

    # Extract refund reason
    reason_prompt = f"""Extract the reason for refund from this customer message: "{query}"

If no specific reason is given, use "Customer requested refund".
Respond with ONLY the reason (max 50 words)."""

    messages = [HumanMessage(content=reason_prompt)]
    reason_response = llm.invoke(messages)
    reason = reason_response.content.strip()

    # Create refund request
    refund_result = create_refund_request(order_id, reason)

    if refund_result.get("success"):
        response = f"""Refund Request Processed ✓

Order ID: #{order_id}
Refund Amount: ${refund_result['refund_amount']:.2f}
Status: PENDING
Reason: {reason}

Your refund has been requested and is pending approval. You will receive a confirmation email shortly.
The refund will typically be processed within 5-7 business days."""

        return {
            "agent_response": response,
            "sql_result": refund_result,
            "is_complete": True,
            "needs_clarification": False,
            "current_agent": "refund_agent",
        }
    else:
        return {
            "agent_response": f"Unable to process refund: {refund_result.get('error')}\n\nPlease contact customer support for assistance.",
            "is_complete": True,
            "needs_clarification": False,
            "current_agent": "refund_agent",
        }


# ==================== ANALYTICS AGENT ====================

def analytics_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Handles analytics and reporting queries.
    Provides sales reports, product insights, and customer statistics.

    Args:
        state: Current conversation state

    Returns:
        Updated state with analytics report
    """
    print("\n[Analytics Agent] Generating report...")

    query = state["user_query"]

    # Determine report type
    if "top product" in query.lower() or "best selling" in query.lower():
        report = get_top_products(limit=5)
        response = "Top 5 Products by Revenue:\n\n"

        for product in report.get("top_products", []):
            response += f"• {product['name']} ({product['category']})\n"
            response += f"  Orders: {product['order_count']}, Revenue: ${product['total_revenue']:.2f}\n"

    elif "customer" in query.lower():
        report = get_customer_stats()
        response = f"Customer Statistics:\n\n"
        response += f"Total Customers: {report.get('total_customers', 0)}\n\n"
        response += "Top Customers by Spending:\n"

        for customer in sorted(
            report.get("customer_stats", []),
            key=lambda x: x["total_spent"],
            reverse=True
        )[:5]:
            response += f"• {customer['name']}: {customer['order_count']} orders, ${customer['total_spent']:.2f} spent\n"

    else:
        # Default: full sales report
        report = get_sales_report()
        response = "Sales Report:\n\n"
        response += f"Total Revenue: ${report.get('total_revenue', 0):.2f}\n"
        response += f"Average Order Value: ${report.get('average_order_value', 0):.2f}\n"
        response += f"Total Orders: {report.get('total_orders', 0)}\n\n"
        response += "Orders by Status:\n"

        for status, count in report.get("order_stats", {}).items():
            response += f"• {status.capitalize()}: {count}\n"

    return {
        "agent_response": response,
        "sql_result": report,
        "is_complete": True,
        "needs_clarification": False,
        "current_agent": "analytics_agent",
    }


# ==================== SUPERVISOR AGENT ====================

def supervisor_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Final validation and formatting of the response.
    Ensures response quality and completeness.

    Args:
        state: Current conversation state

    Returns:
        Final formatted response
    """
    print("\n[Supervisor Agent] Formatting final response...")

    agent_response = state.get("agent_response", "")

    # Add closing message
    final_response = f"""{agent_response}

---
Is there anything else I can help you with today?"""

    return {
        "agent_response": final_response,
        "current_agent": "supervisor_agent",
    }


# ==================== CLARIFICATION AGENT ====================

def clarification_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Asks for clarification when query is unclear.

    Args:
        state: Current conversation state

    Returns:
        Request for clarification
    """
    print("\n[Clarification Agent] Requesting clarification...")

    # Generate helpful clarification prompt
    clarification_prompt = f"""The customer's query was unclear: "{state['user_query']}"

Provide a helpful response asking what they need. Be brief and friendly.
Mention these possible options:
1. Check order status
2. Find product information
3. Process a refund
4. Get business analytics
5. Something else"""

    messages = [HumanMessage(content=clarification_prompt)]
    response = llm.invoke(messages)

    return {
        "agent_response": response.content,
        "is_complete": False,
        "needs_clarification": True,
        "current_agent": "clarification_agent",
    }


# ==================== HUMAN HANDOFF AGENT ====================

def human_handoff_agent(state: CustomerServiceState) -> Dict[str, Any]:
    """
    Escalates to human agent when needed.

    Args:
        state: Current conversation state

    Returns:
        Handoff message to human agent
    """
    print("\n[Human Handoff] Escalating to human agent...")

    response = """I'm escalating your request to our human support team.

A customer service representative will be with you shortly to assist you further.

Thank you for your patience!"""

    return {
        "agent_response": response,
        "is_complete": True,
        "current_agent": "human_handoff",
    }
