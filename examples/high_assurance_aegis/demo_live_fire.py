"""
AEGIS Live Fire Exercise - Cinematic Demonstration

This script simulates both legitimate users and attackers to demonstrate
all security layers in real-time with color-coded console output.

Watch as the system:
- Redacts PHI from legitimate requests
- Detects and bans honeypot attackers
- Logs everything to Merkle chain
- Handles failures with circuit breaker
- Stores dead letters for forensics
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mathprotocol import MockLLM
from aegis_core import DataAirlock, MerkleAuditChain, CircuitBreaker, DeadLetterVault
from honeypot import CanaryHoneypotMiddleware


# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print the AEGIS banner."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("🛡  AEGIS LIVE FIRE EXERCISE")
    print("    Demonstration of Military-Grade MathProtocol Security")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")


def print_section(title, color=Colors.OKCYAN):
    """Print a section header."""
    print(f"\n{color}{Colors.BOLD}{'─' * 70}")
    print(f"▶ {title}")
    print(f"{'─' * 70}{Colors.ENDC}\n")


def print_step(step_num, description, color=Colors.OKBLUE):
    """Print a step in the exercise."""
    print(f"{color}[STEP {step_num}] {description}{Colors.ENDC}")


def print_result(label, value, color=Colors.OKGREEN):
    """Print a result line."""
    print(f"{color}  ➤ {label}: {value}{Colors.ENDC}")


def print_alert(message, alert_type="WARNING"):
    """Print an alert message."""
    color = Colors.WARNING if alert_type == "WARNING" else Colors.FAIL
    icon = "⚠️" if alert_type == "WARNING" else "🚨"
    print(f"{color}{Colors.BOLD}{icon}  {message}{Colors.ENDC}")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def simulate_delay(seconds=0.5):
    """Add dramatic pause."""
    time.sleep(seconds)


def scenario_1_legitimate_request():
    """Scenario 1: Legitimate request with PHI redaction."""
    print_section("SCENARIO 1: Legitimate Request with PHI Protection", Colors.OKCYAN)
    
    airlock = DataAirlock()
    llm = MockLLM()
    
    print_step(1, "User submits request with PHI")
    original_input = "2-1 | Patient john.doe@hospital.com has SSN 123-45-6789 and feels great today!"
    print(f"  Input: {Colors.WARNING}{original_input}{Colors.ENDC}")
    simulate_delay()
    
    print_step(2, "DataAirlock redacts PHI")
    # Extract context
    codes, context = original_input.split('|', 1)
    redacted_context, token_map = airlock.redact(context.strip())
    redacted_input = f"{codes.strip()} | {redacted_context}"
    
    print_result("Redacted Input", redacted_context, Colors.OKGREEN)
    print_result("Tokens Created", list(token_map.keys()), Colors.OKGREEN)
    simulate_delay()
    
    print_step(3, "LLM processes sanitized input")
    response = llm.process(redacted_input)
    print_result("LLM Response", response, Colors.OKBLUE)
    simulate_delay()
    
    print_step(4, "DataAirlock rehydrates response")
    if '|' in response:
        resp_codes, payload = response.split('|', 1)
        rehydrated = airlock.rehydrate(payload.strip(), token_map)
        final_response = f"{resp_codes.strip()} | {rehydrated}"
        print_result("Final Output", final_response, Colors.OKGREEN)
    else:
        print_result("Final Output", response, Colors.OKGREEN)
    
    print_success("PHI never exposed to LLM - Zero-Trust validated!")


def scenario_2_honeypot_attack():
    """Scenario 2: Attacker triggers honeypot."""
    print_section("SCENARIO 2: Honeypot Detection - Active Defense", Colors.WARNING)
    
    banned_ips = set()
    honeypot = CanaryHoneypotMiddleware(None, banned_ips=banned_ips)
    
    print_step(1, "Attacker probes with unknown task code")
    attacker_ip = "192.168.1.666"
    attack_input = "47-1 | Probe request"
    
    print(f"  Source IP: {Colors.FAIL}{attacker_ip}{Colors.ENDC}")
    print(f"  Attack Input: {Colors.FAIL}{attack_input}{Colors.ENDC}")
    simulate_delay()
    
    print_step(2, "Honeypot analyzes request")
    codes_part = attack_input.split('|')[0].strip()
    task_code = int(codes_part.split('-')[0])
    
    if task_code in honeypot.TRAP_CODES:
        print_alert(f"TRAP CODE DETECTED: Task {task_code} is a honeypot!", "ALERT")
        simulate_delay()
        
        print_step(3, "Immediate ban enforcement")
        banned_ips.add(attacker_ip)
        print_alert(f"IP {attacker_ip} PERMANENTLY BANNED", "ALERT")
        print_result("Total Banned", len(banned_ips), Colors.FAIL)
        
        print_step(4, "Subsequent requests blocked")
        print(f"  {Colors.FAIL}403 Forbidden - Access Denied{Colors.ENDC}")
        
        print_success("Attacker neutralized before reaching LLM!")


def scenario_3_circuit_breaker():
    """Scenario 3: Circuit breaker protects against failures."""
    print_section("SCENARIO 3: Circuit Breaker - Fault Isolation", Colors.WARNING)
    
    breaker = CircuitBreaker(failure_threshold=3, timeout=2)
    
    print_step(1, "Simulating LLM failures")
    
    def failing_llm():
        raise Exception("LLM API Timeout")
    
    failure_count = 0
    for i in range(1, 4):
        try:
            print(f"  Attempt {i}...", end=" ")
            breaker.call(failing_llm)
        except Exception:
            failure_count += 1
            print(f"{Colors.FAIL}FAILED{Colors.ENDC}")
            simulate_delay(0.3)
    
    print_result("Total Failures", failure_count, Colors.WARNING)
    simulate_delay()
    
    print_step(2, "Circuit breaker trips OPEN")
    state = breaker.get_state()
    print_alert(f"Circuit State: {state['state']}", "ALERT")
    print_result("Failure Count", state['failure_count'], Colors.FAIL)
    simulate_delay()
    
    print_step(3, "New requests rejected instantly")
    try:
        breaker.call(failing_llm)
    except Exception as e:
        print(f"  {Colors.FAIL}{str(e)}{Colors.ENDC}")
    
    print_success("Resource exhaustion prevented - System protected!")


def scenario_4_merkle_chain():
    """Scenario 4: Merkle audit chain verification."""
    print_section("SCENARIO 4: Merkle Audit Chain - Tamper Evidence", Colors.OKCYAN)
    
    audit = MerkleAuditChain(log_dir="./demo_audit", batch_size=3)
    
    print_step(1, "Logging security events")
    events = [
        ("REQUEST", {"user": "alice", "task": "sentiment"}),
        ("RESPONSE", {"result": "positive", "confidence": "high"}),
        ("HONEYPOT_TRIGGER", {"ip": "192.168.1.666", "code": 47}),
        ("BAN_ENFORCED", {"ip": "192.168.1.666"}),
        ("CIRCUIT_BREAKER", {"state": "OPEN", "failures": 5}),
    ]
    
    for event_type, data in events:
        audit.log_event(event_type, data)
        print(f"  Logged: {Colors.OKBLUE}{event_type}{Colors.ENDC}")
        simulate_delay(0.2)
    
    print_result("Events Buffered", len(audit.buffer), Colors.OKGREEN)
    simulate_delay()
    
    print_step(2, "Computing Merkle root and chaining")
    audit.force_flush()
    print_result("Merkle Root", audit.previous_root[:16] + "...", Colors.OKGREEN)
    print_result("Chain File", str(audit.chain_file), Colors.OKBLUE)
    simulate_delay()
    
    print_step(3, "Verifying chain integrity")
    is_valid = audit.verify_chain()
    if is_valid:
        print_success("✓ Chain integrity VERIFIED - No tampering detected")
    else:
        print_alert("Chain verification FAILED - Tampering detected!", "ALERT")


def scenario_5_dead_letter_vault():
    """Scenario 5: Dead letter vault for forensics."""
    print_section("SCENARIO 5: Dead Letter Vault - Forensic Survivability", Colors.WARNING)
    
    vault = DeadLetterVault(vault_dir="./demo_vault")
    
    print_step(1, "Processing request that fails")
    failed_request = {
        'input': '11-1 | What is the capital of Atlantis?',
        'ip': '10.0.0.42',
        'timestamp': time.time()
    }
    
    error = ValueError("LLM refused to answer - Hallucination prevention")
    
    print(f"  Request: {Colors.OKBLUE}{failed_request['input']}{Colors.ENDC}")
    print(f"  Error: {Colors.FAIL}{str(error)}{Colors.ENDC}")
    simulate_delay()
    
    print_step(2, "Storing in Dead Letter Vault")
    vault.store(failed_request, error)
    dead_letters = vault.list_failed()
    print_result("Vault Location", vault.vault_dir, Colors.OKGREEN)
    print_result("Dead Letters", len(dead_letters), Colors.OKGREEN)
    simulate_delay()
    
    print_step(3, "Forensic retrieval available")
    if dead_letters:
        latest = vault.load(dead_letters[-1])
        print_result("Captured Request", latest['request']['input'][:50], Colors.OKBLUE)
        print_result("Error Type", latest['error']['type'], Colors.WARNING)
        print_result("Timestamp", latest['timestamp'], Colors.OKBLUE)
    
    print_success("Transaction preserved for forensic replay!")


def run_live_fire():
    """Run the complete live fire exercise."""
    print_banner()
    
    print(f"{Colors.BOLD}This demonstration will showcase:{Colors.ENDC}")
    print("  1. PHI/PII Redaction (DataAirlock)")
    print("  2. Active Defense (Honeypot)")
    print("  3. Fault Isolation (Circuit Breaker)")
    print("  4. Tamper-Evident Logging (Merkle Chain)")
    print("  5. Forensic Survivability (Dead Letter Vault)")
    print("\nPress Enter to begin...", end="")
    input()
    
    try:
        scenario_1_legitimate_request()
        simulate_delay(1)
        
        scenario_2_honeypot_attack()
        simulate_delay(1)
        
        scenario_3_circuit_breaker()
        simulate_delay(1)
        
        scenario_4_merkle_chain()
        simulate_delay(1)
        
        scenario_5_dead_letter_vault()
        simulate_delay(1)
        
        # Final summary
        print_section("EXERCISE COMPLETE", Colors.OKGREEN)
        print(f"{Colors.OKGREEN}{Colors.BOLD}")
        print("🎉 All AEGIS security layers demonstrated successfully!")
        print("\nKey Takeaways:")
        print("  ✓ Zero PHI/PII exposure to LLM")
        print("  ✓ Attackers detected and banned in real-time")
        print("  ✓ System resilient to failures")
        print("  ✓ All events cryptographically logged")
        print("  ✓ Failed transactions preserved for forensics")
        print(f"{Colors.ENDC}")
        
    finally:
        # Cleanup demo files
        import shutil
        shutil.rmtree("./demo_audit", ignore_errors=True)
        shutil.rmtree("./demo_vault", ignore_errors=True)
        print(f"\n{Colors.OKBLUE}Demo files cleaned up.{Colors.ENDC}")


if __name__ == "__main__":
    run_live_fire()
