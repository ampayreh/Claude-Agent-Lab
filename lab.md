# Claude Agent Lab: Build a Multi-Skill Agent with Tool Use and Eval

**Time:** 30-45 minutes
**Prerequisites:** Python 3.10+, an Anthropic API key
**What you'll build:** A customer support agent that routes inquiries, looks up orders, and answers policy questions — with a test harness to measure quality.

---

## Setup (5 minutes)

### Step 1: Clone and install

```bash
git clone https://github.com/ampayreh/claude-agent-lab.git
cd claude-agent-lab
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

### Step 2: Verify your setup

```bash
python verify_setup.py
```

You should see:

```
✓ Python 3.10+
✓ anthropic SDK installed
✓ API key set
✓ Test API call succeeded (model: claude-sonnet-4-20250514)
Ready to start the lab.
```

**Checkpoint:** If verify_setup.py passes, you're ready. If not, fix the reported issue before continuing.

---

## Part 1: Your First Tool (10 minutes)

### Step 3: Understand the domain

Open `data.py` and read through it. This is a fictional e-commerce company with:
- **5 customers** with order history
- **10 orders** with items, statuses, and tracking numbers
- **3 return policy rules** (30-day window, electronics 15 days, no swimwear returns)

This is your agent's "database." Everything the agent knows about orders and policies must come from this file via tool calls — not from the system prompt.

### Step 4: Define your first tool

Create a file called `agent.py` and add:

```python
import json
import anthropic
from data import CUSTOMERS, ORDERS, POLICIES

MODEL = "claude-sonnet-4-20250514"

# Tool definitions tell Claude what tools are available and how to call them
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
]
```

### Step 5: Implement the tool

Add the function that executes when Claude calls the tool:

```python
def execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if name == "lookup_order":
        order_id = input_data["order_id"]
        order = ORDERS.get(order_id)
        if order:
            return json.dumps(order, indent=2)
        return json.dumps({"error": f"Order {order_id} not found"})
    return json.dumps({"error": f"Unknown tool: {name}"})
```

### Step 6: Build the agent loop

This is the core pattern: send a message, check if Claude wants to use a tool, execute it, send the result back, repeat.

```python
SYSTEM_PROMPT = """You are a customer support agent for CloudCart, an online retailer.

Rules:
- Always look up order information using the lookup_order tool — never guess
- Be concise and helpful
- If you cannot help, say so honestly
- Do not make up order statuses, tracking numbers, or return policies"""


def run_agent(user_message: str) -> str:
    """Run the agent on a single user message and return the final response."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]

    for _ in range(5):  # Max 5 tool-use rounds
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        # If the model wants to use a tool, execute it and continue
        if response.stop_reason == "tool_use":
            # Add the assistant's response (including tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call and collect results
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

            # Send tool results back to continue the conversation
            messages.append({"role": "user", "content": tool_results})
        else:
            # Model is done — extract and return the text
            return "\n".join(
                block.text for block in response.content if block.type == "text"
            )

    return "Error: too many tool rounds"


if __name__ == "__main__":
    import sys
    question = " ".join(sys.argv[1:]) or "What's the status of order ORD-001?"
    print(f"Question: {question}\n")
    answer = run_agent(question)
    print(f"\nAnswer: {answer}")
```

### Step 7: Test it

```bash
python agent.py "What's the status of order ORD-001?"
```

You should see the agent call `lookup_order` and return details about the order.

**Checkpoint:** The agent should:
1. Call `lookup_order` with `{"order_id": "ORD-001"}`
2. Return a response that includes the order status and items

Try a few more:
```bash
python agent.py "Where is my order ORD-003?"
python agent.py "I need to return something from order ORD-005"
```

---

## Part 2: Multiple Tools (10 minutes)

### Step 8: Add a customer lookup tool

Your agent can look up orders, but what if a customer says "I'm Sarah — what orders do I have?" Add a second tool. Update the `TOOLS` list in `agent.py`:

```python
TOOLS = [
    # ... keep the lookup_order tool from Step 4 ...
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
```

### Step 9: Implement the new tools

Update `execute_tool`:

```python
def execute_tool(name: str, input_data: dict) -> str:
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
        # Check for category-specific policy first, then fall back to general
        policy = POLICIES.get(category) or POLICIES.get("general")
        if policy:
            return json.dumps(policy, indent=2)
        return json.dumps({"error": f"No policy found for '{category}'"})

    return json.dumps({"error": f"Unknown tool: {name}"})
```

### Step 10: Test multi-tool interactions

```bash
python agent.py "I'm Sarah Chen. What's the status of my most recent order?"
```

Watch the tool calls — the agent should:
1. Call `lookup_customer` to find Sarah
2. Call `lookup_order` on her most recent order
3. Combine both results into a coherent answer

Try:
```bash
python agent.py "Can I return the headphones from order ORD-002?"
```

The agent should call both `lookup_order` and `check_return_policy`.

**Checkpoint:** Your agent now chains multiple tool calls in a single conversation turn. This is the core agentic pattern: the model decides which tools to call and in what order.

---

## Part 3: Eval Harness (10 minutes)

### Step 11: Define test cases

Create `eval_cases.json`:

```json
[
    {
        "id": "tc-01",
        "name": "order-status-lookup",
        "input": "What's the status of order ORD-001?",
        "assertions": {
            "must_contain": ["delivered", "ORD-001"],
            "must_not_contain": ["I don't know", "I'm not sure"]
        }
    },
    {
        "id": "tc-02",
        "name": "nonexistent-order",
        "input": "Where is order ORD-999?",
        "assertions": {
            "must_contain": ["not found"],
            "must_not_contain": ["delivered", "shipped", "tracking"]
        }
    },
    {
        "id": "tc-03",
        "name": "return-policy-electronics",
        "input": "Can I return the headphones from order ORD-002?",
        "assertions": {
            "must_contain": ["15", "day"],
            "must_not_contain": ["30 day"]
        }
    },
    {
        "id": "tc-04",
        "name": "customer-lookup",
        "input": "I'm Sarah Chen, what orders do I have?",
        "assertions": {
            "must_contain": ["ORD-001"],
            "must_not_contain": ["ORD-003", "ORD-004"]
        }
    },
    {
        "id": "tc-05",
        "name": "no-hallucination",
        "input": "What's the CEO's phone number?",
        "assertions": {
            "must_contain_any": ["can't", "cannot", "don't have", "not able"],
            "must_not_contain": ["555", "phone", "number is"]
        }
    }
]
```

### Step 12: Build the eval runner

Create `eval_runner.py`:

```python
#!/usr/bin/env python3
"""Eval harness for the CloudCart support agent."""

import json
import sys
import time

from agent import run_agent


def load_cases(path: str = "eval_cases.json") -> list:
    with open(path) as f:
        return json.load(f)


def grade(response: str, assertions: dict) -> dict:
    """Grade a response against deterministic assertions."""
    response_lower = response.lower()
    failures = []

    for term in assertions.get("must_contain", []):
        if term.lower() not in response_lower:
            failures.append(f"MISSING: '{term}'")

    for term in assertions.get("must_not_contain", []):
        if term.lower() in response_lower:
            failures.append(f"UNEXPECTED: '{term}'")

    if "must_contain_any" in assertions:
        if not any(t.lower() in response_lower
                   for t in assertions["must_contain_any"]):
            failures.append(
                f"MISSING_ANY: none of {assertions['must_contain_any']}"
            )

    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }


def run_eval(cases_path: str = "eval_cases.json", runs: int = 1):
    """Run the eval suite."""
    cases = load_cases(cases_path)
    all_results = []

    for run_idx in range(runs):
        print(f"\n{'='*50}")
        print(f"Run {run_idx + 1}/{runs}")
        print(f"{'='*50}")

        for case in cases:
            print(f"\n  {case['id']}: {case['name']}...", end=" ", flush=True)

            t0 = time.monotonic()
            try:
                response = run_agent(case["input"])
            except Exception as e:
                response = f"ERROR: {e}"
            latency = time.monotonic() - t0

            result = grade(response, case["assertions"])
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} ({latency:.1f}s)")

            if not result["passed"]:
                for f in result["failures"]:
                    print(f"    {f}")

            all_results.append({
                "run": run_idx,
                "case_id": case["id"],
                "name": case["name"],
                "passed": result["passed"],
                "failures": result["failures"],
                "response_excerpt": response[:200],
                "latency_s": round(latency, 2),
            })

    # Summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")

    # Per-case pass rate across runs
    if runs > 1:
        print(f"\nPer-case pass rate ({runs} runs):")
        for case in cases:
            case_results = [r for r in all_results if r["case_id"] == case["id"]]
            case_passed = sum(1 for r in case_results if r["passed"])
            print(f"  {case['id']} {case['name']}: {case_passed}/{runs}")

    # Write results
    with open("eval_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results: eval_results.json")


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_eval(runs=runs)
```

### Step 13: Run the eval

```bash
python eval_runner.py
```

All 5 cases should pass. Run 3 times to check consistency:

```bash
python eval_runner.py 3
```

**Checkpoint:** You now have a repeatable, automated quality measurement for your agent. This is the pattern used in production: define expected behaviors as assertions, run them on every change, track pass rates over time.

---

## Part 4: Extend It (5 minutes, optional)

Ideas for extending the lab on your own:

1. **Add an LLM judge** — for test case tc-05, the "no hallucination" check uses keyword matching. Write a judge that uses a separate Claude call to score whether the response appropriately declines.

2. **Add a new tool** — implement `create_return_request` that writes a return to a list. Add a test case that verifies the tool is called with the right order ID.

3. **Add conversation history** — modify `run_agent` to accept a list of prior messages, enabling multi-turn conversations.

4. **Track costs** — add token counting from `response.usage` and report per-case cost in the eval output.

---

## What You Built

| Component | Pattern | File |
|-----------|---------|------|
| Tool definitions | JSON schema describing available tools | `agent.py` |
| Tool execution | Dispatch function matching tool names to implementations | `agent.py` |
| Agent loop | Send → check stop_reason → execute tool → send result → repeat | `agent.py` |
| Multi-tool chaining | Model decides tool order based on the question | `agent.py` |
| Deterministic eval | Assertions on must_contain / must_not_contain | `eval_runner.py` |
| Variance measurement | Multiple runs to detect flaky behavior | `eval_runner.py` |

These are the same patterns used in production Claude deployments at scale. The ScopingAgent repo in this portfolio uses progressive disclosure across 4 pipeline steps with tool use; the LMMSmartClinicAI repo uses intent routing + formulary search + guardrails + clinical safety evals. This lab teaches the foundational building blocks.

---

## Instructor Notes

### Common failure points

1. **Missing `tool_result` message.** Students forget to send tool results back after executing the tool. The API returns an error about expected message roles.

2. **Not handling `stop_reason`.** The check `if response.stop_reason == "tool_use"` is essential. Without it, the agent tries to parse tool_use blocks as text.

3. **Tool name mismatch.** The `name` in the tool definition must exactly match what `execute_tool` dispatches on. A typo means the tool is defined but never executes.

4. **Infinite loops.** Without the `for _ in range(5)` guard, a confused model can keep calling tools forever. Always cap the loop.

5. **Eval brittleness.** `must_contain` assertions are case-insensitive but exact substring matches. "delivered" matches "Delivered" but not "has been deliver". Coach students to pick assertions that are robust to phrasing variation.

### Timing

| Part | Target | Buffer |
|------|--------|--------|
| Setup | 5 min | +2 min for pip issues |
| Part 1 (first tool) | 10 min | +5 min for debugging |
| Part 2 (multi-tool) | 10 min | +3 min |
| Part 3 (eval) | 10 min | +5 min for first run |
| Part 4 (extend) | 5 min | Optional |
| **Total** | **40 min** | **55 min max** |
