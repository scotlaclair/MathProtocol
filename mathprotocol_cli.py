#!/usr/bin/env python3
"""
MathProtocol V2 CLI Tool

A command-line interface for composing protocol prompts and
introspecting the protocol registry.
"""

import argparse
import sys
from typing import List
from mathprotocol import MathProtocol, registry


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="MathProtocol V2 CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all registered codes
  %(prog)s list
  
  # Compose a translation request
  %(prog)s compose --task 17 --params 1 2 --context "Hello World"
  
  # Compose with file content
  %(prog)s compose --task 11 --params 3 --context @/path/to/file.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # LIST command - introspect registry
    subparsers.add_parser(
        "list", 
        help="List all registered Tasks, Parameters, and Response Codes"
    )
    
    # COMPOSE command - construct prompts
    compose_parser = subparsers.add_parser(
        "compose", 
        help="Compose a protocol prompt"
    )
    compose_parser.add_argument(
        "--task", 
        type=int, 
        required=True, 
        help="Task Prime ID"
    )
    compose_parser.add_argument(
        "--params", 
        type=int, 
        nargs="+", 
        default=[1], 
        help="Parameter Fibonacci IDs (space-separated)"
    )
    compose_parser.add_argument(
        "--context", 
        type=str, 
        required=True, 
        help="Context string or filepath (prefix with @ to read from file)"
    )

    args = parser.parse_args()
    protocol = MathProtocol()

    if args.command == "list":
        print_registry()
    elif args.command == "compose":
        compose_prompt(protocol, args.task, args.params, args.context)
    else:
        parser.print_help()
        sys.exit(1)


def print_registry():
    """Print all registered protocol codes."""
    print("\n" + "=" * 70)
    print("MathProtocol V2 Registry")
    print("=" * 70)
    
    # Tasks
    print("\n📋 REGISTERED TASKS (Primes):")
    print("-" * 70)
    tasks = sorted(registry.tasks.items())
    for prime, name in tasks:
        print(f"  {prime:3d} → {name}")
    
    # Parameters
    print("\n⚙️  REGISTERED PARAMETERS (Fibonacci):")
    print("-" * 70)
    params = sorted(registry.parameters.items())
    for fib, name in params:
        print(f"  {fib:3d} → {name}")
    
    # Responses
    print("\n📤 REGISTERED RESPONSE CODES (Powers of 2):")
    print("-" * 70)
    responses = sorted(registry.responses.items())
    for power, name in responses:
        print(f"  {power:4d} → {name}")
    
    print("\n" + "=" * 70 + "\n")


def compose_prompt(protocol: MathProtocol, task: int, params: List[int], context: str):
    """
    Compose a protocol prompt.
    
    Args:
        protocol: MathProtocol instance
        task: Task prime number
        params: List of parameter fibonacci numbers
        context: Context string or filepath (with @ prefix)
    """
    # Handle file input
    if context.startswith("@"):
        filepath = context[1:]
        try:
            with open(filepath, 'r') as f:
                context = f.read()
            print(f"✓ Loaded context from: {filepath}")
        except FileNotFoundError:
            print(f"❌ Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Validate request
    if not protocol.validate_request(task, params):
        print(f"❌ Error: Invalid task or parameters", file=sys.stderr)
        print(f"\nTask {task}: {registry.get_task_name(task)}", file=sys.stderr)
        for p in params:
            print(f"Param {p}: {registry.get_parameter_name(p)}", file=sys.stderr)
        sys.exit(1)
    
    # Construct prompt
    prompt = protocol.construct_prompt(task, params, context)
    
    # Display metadata
    print("\n" + "=" * 70)
    print("MathProtocol V2 Prompt Composer")
    print("=" * 70)
    print(f"\n📋 Task: {task} ({registry.get_task_name(task)})")
    
    param_names = [f"{p}({registry.get_parameter_name(p)})" for p in params]
    print(f"⚙️  Parameters: {', '.join(param_names)}")
    
    checksum = task * sum(params)
    print(f"🔒 Checksum: {checksum}")
    print(f"📝 Context Length: {len(context)} chars")
    
    print("\n" + "-" * 70)
    print("Generated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    
    # Validation reminder
    print("\n💡 Reminder: LLM response should be a single integer response code")
    print("   Example: 128 (High Confidence)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
