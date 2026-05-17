"""
Agent: Addition
Purpose: Adds two numbers and returns the result.
Usage:  python agent-addition.py <num1> <num2>
        python agent-addition.py          # prompts interactively
"""

import sys


def add(a: float, b: float) -> float:
    return a + b


def parse_number(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number: '{value}'")


def main():
    if len(sys.argv) == 3:
        a = parse_number(sys.argv[1])
        b = parse_number(sys.argv[2])
    else:
        a = parse_number(input("Enter first number: ").strip())
        b = parse_number(input("Enter second number: ").strip())

    result = add(a, b)

    print(f"\n{a} + {b} = {result}")
    return result


if __name__ == "__main__":
    main()
