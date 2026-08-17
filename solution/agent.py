#!/usr/bin/env python3
"""
CloudCart Support Agent — Complete Solution

Multi-tool agent with order lookup, customer lookup, and return
policy checking. Uses Claude's tool-use capability to ground
every answer in actual data.
"""

import json
import sys

import anthropic

# Import from parent directory
sys.path.insert(0, "..")
from data import CUSTOMERS, ORDERS, POLICIES


MODEL = "claude-sonnet-4-20250514"

TOOLS = [
    {
        "name": "lookup_order",
        "description": (
            "Look up an order by order ID. Returns order details including "
            "items, status, shipping, and total. Use this when a customer "
            "asks about a specific order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID (e.g., 'ORD-001')",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "lookup_customer",
        "description": (
            "Look up a customer by name or email. Returns their profile "
            "and order history. Use this when a customer identifies "
            "themselves and you need to find their orders."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Customer name or email address",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_return_policy",
        "description": (
            "Check the return policy for a given product category. "
            "Returns eligibility rules and time limits. Use this when "
            "a customer asks about returns, refunds, or exchanges."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "Product category to check. Use 'general' for the "
                        "default policy, or a specific category like "
                        "'electronics' or 'swimwear'."
                    ),
                }
            },
            "required": ["category"],
        },
    },
]

SYSTEM_PROMPT = """You are a customer support agent for CloudCart, an online retailer.

Rules:
- Always look up order information using the lookup_order tool — never guess
- Be concise and helpful
- If you cannot help, say so honestly
- Do not make up order statuses, tracking numbers, or return policies"""


def execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if name == "lookup_order":
        order_id = input_data["order_id"]
        order = ORDERS.get(order_id)
        if order:
            return json.dumps(order, indent=2)
        return json.dumps({"error": f"Order {order_id} not found"})

    elif name == "lookup_customer":
        query = input_data["query"].lower()
        for cust_id, customer in CUSTOMERS.items():
            if (query in customer["name"].lower()
                    or query in customer["email"].lower()):
                return json.dumps(customer, indent=2)
        return json.dumps({"error": f"No customer matching '{input_data['query']}'"})

    elif name == "check_return_policy":
        category = input_data["category"].lower()
        policy = POLICIES.get(category) or POLICIES.get("general")
        if policy:
            return json.dumps(policy, indent=2)
        return json.dumps({"error": f"No policy found for '{category}'"})

    return json.dumps({"error": f"Unknown tool: {name}"})


def run_agent(user_message: str) -> str:
    """Run the agent on a single user message and return the final response."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]

    for _ in range(5):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  Tool: {block.name}({block.input})")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            return "\n".join(
                block.text for block in response.content if block.type == "text"
            )

    return "Error: too many tool rounds"


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What's the status of order ORD-001?"
    print(f"Question: {question}\n")
    answer = run_agent(question)
    print(f"\nAnswer: {answer}")
