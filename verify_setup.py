#!/usr/bin/env python3
"""Verify lab prerequisites are met."""

import os
import sys


def check_python():
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 10
    status = "✓" if ok else "✗"
    print(f"{status} Python {v.major}.{v.minor}.{v.micro}" +
          ("" if ok else " (need 3.10+)"))
    return ok


def check_anthropic():
    try:
        import anthropic  # noqa: F401
        print("✓ anthropic SDK installed")
        return True
    except ImportError:
        print("✗ anthropic SDK not installed (run: pip install anthropic)")
        return False


def check_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        print("✓ API key set")
        return True
    print("✗ ANTHROPIC_API_KEY not set")
    return False


def check_api_call():
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'ok'"}],
        )
        model = response.model
        print(f"✓ Test API call succeeded (model: {model})")
        return True
    except Exception as e:
        print(f"✗ API call failed: {e}")
        return False


def main():
    checks = [check_python(), check_anthropic(), check_api_key()]
    if all(checks):
        checks.append(check_api_call())

    if all(checks):
        print("\nReady to start the lab.")
    else:
        print("\nFix the issues above before starting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
