#!/usr/bin/env python3
"""
Audit Log Disassembler for MathProtocol Aegis Module

This CLI tool parses Merkle-chained audit logs and provides
human-readable output with color coding for threat levels.
"""

import json
import sys
import argparse
from datetime import datetime
from mathprotocol import registry


# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def parse_log_line(line: str) -> str:
    """
    Parse a single log line and format it for display.
    
    Args:
        line: JSON string from the audit log
        
    Returns:
        Formatted string with decoded information and color coding
    """
    try:
        entry = json.loads(line)
        
        # Extract common fields
        timestamp = entry.get('timestamp', 0)
        dt = datetime.fromtimestamp(timestamp)
        event = entry.get('event', 'UNKNOWN')
        threat_score = entry.get('threat_score', 0)
        
        # Color code based on threat level
        if threat_score >= 5:
            color = Colors.RED
            threat_label = "CRITICAL"
        elif threat_score >= 2:
            color = Colors.YELLOW
            threat_label = "HIGH"
        elif threat_score > 0:
            color = Colors.YELLOW
            threat_label = "MEDIUM"
        else:
            color = Colors.GREEN
            threat_label = "NORMAL"
        
        # Build output
        output = f"{Colors.BOLD}[{dt.strftime('%Y-%m-%d %H:%M:%S')}]{Colors.RESET} "
        output += f"{color}{event}{Colors.RESET} "
        output += f"(Threat: {color}{threat_label}{Colors.RESET})\n"
        
        # Decode task if present
        if 'task_prime' in entry:
            task_prime = entry['task_prime']
            task_name = registry.get_task_name(task_prime)
            output += f"  {Colors.CYAN}Task:{Colors.RESET} {task_prime} ({task_name})\n"
        
        # Decode params if present
        if 'params_fib' in entry:
            params = entry['params_fib']
            param_names = [f"{p}({registry.get_parameter_name(p)})" for p in params]
            output += f"  {Colors.CYAN}Params:{Colors.RESET} {', '.join(param_names)}\n"
        
        # Add client IP
        if 'client_ip' in entry:
            output += f"  {Colors.CYAN}Client:{Colors.RESET} {entry['client_ip']}\n"
        
        # Add validation status
        if 'valid' in entry:
            valid_str = f"{Colors.GREEN}VALID{Colors.RESET}" if entry['valid'] else f"{Colors.RED}INVALID{Colors.RESET}"
            output += f"  {Colors.CYAN}Validation:{Colors.RESET} {valid_str}\n"
        
        # Add context sample if present
        if 'context_sample' in entry:
            sample = entry['context_sample']
            output += f"  {Colors.CYAN}Context Sample:{Colors.RESET} {sample}...\n"
        
        # Add message if present
        if 'message' in entry:
            output += f"  {Colors.CYAN}Message:{Colors.RESET} {entry['message']}\n"
        
        # Add Merkle chain info
        merkle_hash = entry.get('merkle_hash', 'N/A')[:16]
        prev_hash = entry.get('prev_hash', 'N/A')[:16]
        output += f"  {Colors.MAGENTA}Chain:{Colors.RESET} {merkle_hash}... <- {prev_hash}...\n"
        
        return output
        
    except json.JSONDecodeError:
        return f"{Colors.RED}[ERROR]{Colors.RESET} Could not parse line: {line[:50]}...\n"
    except Exception as e:
        return f"{Colors.RED}[ERROR]{Colors.RESET} {str(e)}\n"


def main():
    """Main entry point for the audit viewer."""
    parser = argparse.ArgumentParser(
        description="MathProtocol Audit Log Disassembler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s aegis_audit.jsonl
  %(prog)s aegis_audit.jsonl --filter-threats
  %(prog)s /var/log/aegis/audit.jsonl --filter-threats
        """
    )
    parser.add_argument("logfile", help="Path to the JSONL audit log file")
    parser.add_argument(
        "--filter-threats", 
        action="store_true", 
        help="Only show entries with threat_score > 0"
    )
    
    args = parser.parse_args()
    
    try:
        # Print header
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}MathProtocol Aegis Audit Log{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")
        print(f"Log File: {args.logfile}")
        if args.filter_threats:
            print(f"Filter: {Colors.YELLOW}Threats Only{Colors.RESET}")
        print(f"{Colors.BOLD}{'-' * 70}{Colors.RESET}\n")
        
        # Parse and display log entries
        entry_count = 0
        displayed_count = 0
        
        with open(args.logfile, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                entry_count += 1
                
                # Parse JSON first for filtering
                try:
                    entry = json.loads(line)
                    threat_score = entry.get("threat_score", 0)
                    
                    # Apply filter if requested
                    if args.filter_threats and threat_score == 0:
                        continue
                    
                    # Display the entry
                    print(parse_log_line(line))
                    displayed_count += 1
                    
                except json.JSONDecodeError:
                    print(f"{Colors.RED}[ERROR]{Colors.RESET} Malformed entry at line {entry_count}\n")
        
        # Print summary
        print(f"{Colors.BOLD}{'-' * 70}{Colors.RESET}")
        print(f"Total Entries: {entry_count}")
        print(f"Displayed: {displayed_count}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")
        
    except FileNotFoundError:
        print(f"{Colors.RED}Error:{Colors.RESET} Log file '{args.logfile}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error:{Colors.RESET} {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
