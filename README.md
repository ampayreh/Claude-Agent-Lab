# Claude Agent Lab

A 30-45 minute hands-on lab that teaches how to build a multi-tool Claude agent with an eval harness. You'll build a customer support agent from scratch — defining tools, implementing the agent loop, chaining multiple tool calls, and measuring quality with deterministic assertions.

## What You'll Build

A **CloudCart support agent** that:
- Looks up orders by ID
- Finds customers by name or email
- Checks return policies by product category
- Chains multiple tools in a single turn (e.g., find customer → look up their order → check return policy)
- Refuses to hallucinate information it doesn't have

Plus an **eval harness** with 5 test cases that verify the agent works correctly.

## Prerequisites

- Python 3.10+
- An Anthropic API key (`ANTHROPIC_API_KEY`)
- ~$0.50 in API credits (the full lab uses ~20-30 API calls)

## Quickstart

```bash
git clone https://github.com/ampayreh/claude-agent-lab.git
cd claude-agent-lab
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python verify_setup.py
```

Then open [lab.md](lab.md) and follow the instructions.

## Structure

```
claude-agent-lab/
├── lab.md               # The lab instructions (start here)
├── data.py              # Fictional e-commerce data (customers, orders, policies)
├── verify_setup.py      # Setup verification script
├── requirements.txt     # Dependencies (anthropic SDK only)
├── solution/
│   ├── agent.py         # Complete working agent
│   ├── eval_cases.json  # Test cases
│   └── eval_runner.py   # Eval harness
└── README.md
```

## Lab Outline

| Part | What you build | Time |
|------|---------------|------|
| **Setup** | Verify Python, SDK, API key | 5 min |
| **Part 1** | Single tool (order lookup) + agent loop | 10 min |
| **Part 2** | Multi-tool (customer + policy) + chaining | 10 min |
| **Part 3** | Eval harness with 5 test cases | 10 min |
| **Part 4** | Extensions (optional: LLM judge, new tools, multi-turn) | 5 min |

## Patterns Taught

| Pattern | Where |
|---------|-------|
| Tool definition (JSON Schema) | Part 1, Step 4 |
| Tool execution dispatch | Part 1, Step 5 |
| Agent loop (send → tool_use → execute → result → repeat) | Part 1, Step 6 |
| Multi-tool chaining (model decides order) | Part 2, Step 10 |
| Deterministic eval (must_contain / must_not_contain) | Part 3, Step 11 |
| Variance measurement (multiple runs) | Part 3, Step 13 |

These are the same patterns used in production. The [ScopingAgent](https://github.com/ampayreh/ScopingAgent) repo in this portfolio uses progressive disclosure across 4 pipeline steps with tool use; the [LMMSmartClinicAI](https://github.com/ampayreh/LMMSmartClinicAI) repo uses intent routing + formulary search + guardrails + clinical safety evals.

## Running the Solution

If you want to see the finished product without building it yourself:

```bash
cd solution
python agent.py "What's the status of order ORD-001?"
python agent.py "I'm Sarah Chen, what orders do I have?"
python agent.py "Can I return the swim goggles from order ORD-005?"
python eval_runner.py 3    # Run eval suite 3 times
```

## Author

**Graeme Tobias Ampeire** — MSIS Candidate, UW Foster School of Business (2026)
