"""
AEGIS Core Security Modules - Merkle Edition

This module implements four critical security components:
1. DataAirlock - PHI/PII Redaction (HIPAA Compliance)
2. MerkleAuditChain - Tamper-Evident Logging (NIST AU-9)
3. CircuitBreaker - Fault Isolation (NIST SC-7)
4. DeadLetterVault - Forensic Survivability (NIST AU-11)

All components are production-ready and thread-safe.
"""

import re
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from threading import Lock
import traceback


class DataAirlock:
    """
    Implements HIPAA-compliant PHI/PII redaction before data reaches the LLM.
    
    Scans for sensitive patterns (Email, SSN, MRN, Phone) and replaces them
    with deterministic tokens. Original values can be re-hydrated after
    LLM processing.
    
    Security Control: HIPAA § 164.514(b) - De-identification
    """
    
    # Regex patterns for sensitive data
    PATTERNS = {
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'MRN': r'\bMRN[-:]?\s*\d{6,10}\b',
        'CREDIT_CARD': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }
    
    def __init__(self):
        self.vault: Dict[str, str] = {}  # Token -> Original Value
        self.counter: Dict[str, int] = {}  # Pattern -> Counter
        self.lock = Lock()
    
    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Scan and redact sensitive data from text.
        
        Args:
            text: Input text that may contain PHI/PII
            
        Returns:
            Tuple of (redacted_text, token_map)
        """
        with self.lock:
            redacted = text
            token_map = {}
            
            for pattern_name, pattern in self.PATTERNS.items():
                matches = re.findall(pattern, text)
                for match in matches:
                    # Generate deterministic token
                    if pattern_name not in self.counter:
                        self.counter[pattern_name] = 0
                    self.counter[pattern_name] += 1
                    
                    token = f"<{pattern_name}_{self.counter[pattern_name]}>"
                    
                    # Store mapping
                    self.vault[token] = match
                    token_map[token] = match
                    
                    # Replace in text
                    redacted = redacted.replace(match, token)
            
            return redacted, token_map
    
    def rehydrate(self, text: str, token_map: Optional[Dict[str, str]] = None) -> str:
        """
        Restore original values from tokens.
        
        Args:
            text: Redacted text with tokens
            token_map: Optional specific token map (uses vault if None)
            
        Returns:
            Original text with sensitive data restored
        """
        with self.lock:
            rehydrated = text
            tokens = token_map if token_map is not None else self.vault
            
            for token, original in tokens.items():
                rehydrated = rehydrated.replace(token, original)
            
            return rehydrated
    
    def clear_vault(self):
        """Clear the vault (for testing or periodic cleanup)."""
        with self.lock:
            self.vault.clear()
            self.counter.clear()


class MerkleAuditChain:
    """
    Implements batched, cryptographically-chained audit logging.
    
    Instead of writing each log entry individually, events are buffered
    in memory. When the buffer reaches threshold, a Merkle root is computed
    and chained to the previous root, then batch-written to disk.
    
    Security Control: NIST AU-9 (Audit Log Protection)
    """
    
    def __init__(self, log_dir: str = "./audit_logs", batch_size: int = 10):
        """
        Initialize Merkle Audit Chain.
        
        Args:
            log_dir: Directory for audit log files
            batch_size: Number of events before batch write
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        self.batch_size = batch_size
        self.buffer: List[Dict[str, Any]] = []
        self.previous_root = "GENESIS"
        self.chain_file = self.log_dir / "merkle_chain.jsonl"
        self.lock = Lock()
        
        # Load previous root if exists
        if self.chain_file.exists():
            with open(self.chain_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    self.previous_root = last_entry.get('merkle_root', 'GENESIS')
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event to the audit chain.
        
        Args:
            event_type: Type of event (e.g., "REQUEST", "RESPONSE", "ERROR")
            data: Event data
        """
        with self.lock:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'data': data
            }
            self.buffer.append(event)
            
            # Flush if buffer is full
            if len(self.buffer) >= self.batch_size:
                self._flush()
    
    def _compute_merkle_root(self, events: List[Dict[str, Any]]) -> str:
        """
        Compute Merkle root of event list.
        
        Args:
            events: List of events
            
        Returns:
            Merkle root hash (hex string)
        """
        if not events:
            return hashlib.sha256(b"EMPTY").hexdigest()
        
        # Hash each event
        hashes = [
            hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
            for event in events
        ]
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last hash if odd
            
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level
        
        return hashes[0]
    
    def _flush(self):
        """Flush buffer to disk with Merkle root chaining."""
        if not self.buffer:
            return
        
        # Compute Merkle root
        merkle_root = self._compute_merkle_root(self.buffer)
        
        # Chain to previous root
        chain_hash = hashlib.sha256(
            (self.previous_root + merkle_root).encode()
        ).hexdigest()
        
        # Create batch entry
        batch_entry = {
            'batch_id': int(time.time() * 1000),
            'previous_root': self.previous_root,
            'merkle_root': merkle_root,
            'chain_hash': chain_hash,
            'event_count': len(self.buffer),
            'events': self.buffer.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Write to chain file
        with open(self.chain_file, 'a') as f:
            f.write(json.dumps(batch_entry) + '\n')
        
        # Update state
        self.previous_root = merkle_root
        self.buffer.clear()
    
    def force_flush(self):
        """Force flush buffer (for shutdown or testing)."""
        with self.lock:
            self._flush()
    
    def verify_chain(self) -> bool:
        """
        Verify integrity of the entire chain.
        
        Returns:
            True if chain is intact, False if tampered
        """
        if not self.chain_file.exists():
            return True  # No chain yet
        
        with open(self.chain_file, 'r') as f:
            entries = [json.loads(line) for line in f]
        
        if not entries:
            return True
        
        # Verify each link
        for i, entry in enumerate(entries):
            # Recompute Merkle root
            computed_root = self._compute_merkle_root(entry['events'])
            if computed_root != entry['merkle_root']:
                return False
            
            # Verify chain hash
            if i == 0:
                expected_prev = "GENESIS"
            else:
                expected_prev = entries[i - 1]['merkle_root']
            
            if entry['previous_root'] != expected_prev:
                return False
            
            # Verify chain hash computation
            expected_chain = hashlib.sha256(
                (entry['previous_root'] + entry['merkle_root']).encode()
            ).hexdigest()
            if entry['chain_hash'] != expected_chain:
                return False
        
        return True


class CircuitBreaker:
    """
    Implements fault isolation to prevent cascade failures.
    
    Tracks failure rate and automatically "trips" to reject requests
    when error threshold is exceeded. Prevents resource exhaustion.
    
    Security Control: NIST SC-7 (Boundary Protection)
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize Circuit Breaker.
        
        Args:
            failure_threshold: Number of failures before tripping
            timeout: Seconds before attempting reset
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = Lock()
    
    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is OPEN or function fails
        """
        with self.lock:
            # Check if circuit is OPEN
            if self.state == "OPEN":
                # Check if timeout has passed
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN - Service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN
            with self.lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
            
            raise e
    
    def reset(self):
        """Manually reset circuit breaker."""
        with self.lock:
            self.state = "CLOSED"
            self.failure_count = 0
            self.last_failure_time = 0
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        with self.lock:
            return {
                'state': self.state,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time
            }


class DeadLetterVault:
    """
    Implements forensic transaction storage for failed requests.
    
    When the circuit breaker trips or LLM fails, the full request
    context is serialized to disk for later replay/analysis.
    
    Security Control: NIST AU-11 (Audit Record Retention)
    """
    
    def __init__(self, vault_dir: str = "./dead_letter_vault"):
        """
        Initialize Dead Letter Vault.
        
        Args:
            vault_dir: Directory for dead letter files
        """
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(exist_ok=True, parents=True)
        self.lock = Lock()
    
    def store(self, request_data: Dict[str, Any], error: Exception):
        """
        Store failed transaction with full context.
        
        Args:
            request_data: Original request data
            error: Exception that caused failure
        """
        with self.lock:
            timestamp = datetime.utcnow().isoformat().replace(':', '-')
            filename = f"dead_letter_{timestamp}_{id(request_data)}.json"
            filepath = self.vault_dir / filename
            
            # Capture full error context
            dead_letter = {
                'timestamp': datetime.utcnow().isoformat(),
                'request': request_data,
                'error': {
                    'type': type(error).__name__,
                    'message': str(error),
                    'traceback': traceback.format_exc()
                }
            }
            
            # Write to vault
            with open(filepath, 'w') as f:
                json.dump(dead_letter, f, indent=2)
    
    def list_failed(self) -> List[str]:
        """
        List all failed transactions.
        
        Returns:
            List of dead letter file paths
        """
        return [str(f) for f in self.vault_dir.glob("dead_letter_*.json")]
    
    def load(self, filepath: str) -> Dict[str, Any]:
        """
        Load a specific dead letter for replay.
        
        Args:
            filepath: Path to dead letter file
            
        Returns:
            Dead letter data
        """
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def clear_vault(self):
        """Clear all dead letters (for testing)."""
        with self.lock:
            for file in self.vault_dir.glob("dead_letter_*.json"):
                file.unlink()


# Security Validation Functions

def validate_aegis_security():
    """
    Run comprehensive security validation tests.
    
    Returns:
        True if all tests pass
    """
    print("=" * 60)
    print("AEGIS SECURITY VALIDATION")
    print("=" * 60)
    
    # Test 1: DataAirlock PHI Redaction
    print("\n[TEST 1] DataAirlock PHI Redaction")
    airlock = DataAirlock()
    phi_text = "Patient John Doe, SSN 123-45-6789, email john.doe@hospital.com"
    redacted, tokens = airlock.redact(phi_text)
    
    print(f"Original: {phi_text}")
    print(f"Redacted: {redacted}")
    
    assert "123-45-6789" not in redacted, "SSN not redacted!"
    assert "john.doe@hospital.com" not in redacted, "Email not redacted!"
    assert "<SSN_1>" in redacted, "SSN token missing!"
    assert "<EMAIL_1>" in redacted, "Email token missing!"
    print("✓ PASS: PHI successfully redacted")
    
    # Test 2: DataAirlock Rehydration
    print("\n[TEST 2] DataAirlock Rehydration")
    rehydrated = airlock.rehydrate(redacted, tokens)
    assert rehydrated == phi_text, "Rehydration failed!"
    print(f"Rehydrated: {rehydrated}")
    print("✓ PASS: PHI successfully rehydrated")
    
    # Test 3: Merkle Chain Integrity
    print("\n[TEST 3] Merkle Chain Integrity")
    audit = MerkleAuditChain(log_dir="./test_audit", batch_size=3)
    
    for i in range(5):
        audit.log_event("TEST", {"index": i, "data": f"Event {i}"})
    
    audit.force_flush()
    
    is_valid = audit.verify_chain()
    assert is_valid, "Merkle chain verification failed!"
    print("✓ PASS: Merkle chain integrity verified")
    
    # Test 4: Circuit Breaker
    print("\n[TEST 4] Circuit Breaker")
    breaker = CircuitBreaker(failure_threshold=3, timeout=1)
    
    def failing_function():
        raise ValueError("Simulated failure")
    
    # Trigger failures
    for i in range(3):
        try:
            breaker.call(failing_function)
        except:
            pass
    
    state = breaker.get_state()
    assert state['state'] == "OPEN", "Circuit breaker should be OPEN!"
    print(f"State: {state['state']}, Failures: {state['failure_count']}")
    print("✓ PASS: Circuit breaker tripped correctly")
    
    # Test 5: Dead Letter Vault
    print("\n[TEST 5] Dead Letter Vault")
    vault = DeadLetterVault(vault_dir="./test_vault")
    
    request = {"task": "test", "input": "sample"}
    error = ValueError("Test error")
    vault.store(request, error)
    
    failed = vault.list_failed()
    assert len(failed) > 0, "Dead letter not stored!"
    print(f"Stored {len(failed)} dead letter(s)")
    print("✓ PASS: Dead letter stored successfully")
    
    # Cleanup
    import shutil
    shutil.rmtree("./test_audit", ignore_errors=True)
    shutil.rmtree("./test_vault", ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("ALL SECURITY TESTS PASSED ✓")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    validate_aegis_security()
