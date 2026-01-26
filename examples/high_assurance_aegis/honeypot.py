"""
Honeypot Middleware - Active Defense for MathProtocol

This module implements canary-based intrusion detection using invalid
protocol codes as honeypots. Any client using these codes is automatically
banned as they are probing the system.

Security Control: NIST SI-4 (Information System Monitoring)
"""

from typing import Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


class CanaryHoneypotMiddleware(BaseHTTPMiddleware):
    """
    Active defense middleware using canary task codes.
    
    Certain prime numbers (43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97)
    are designated as trap codes. They are valid primes but not assigned
    to any task in MathProtocol.
    
    If a client uses these codes, they are:
    1. Logged as suspicious
    2. Banned permanently
    3. Returned a 403 Forbidden
    
    This detects automated probing attempts.
    """
    
    # Trap codes - Valid primes but NOT in TASKS mapping
    TRAP_CODES = {43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    
    # Parameter honeypots - Valid Fibonacci but unusual combinations
    # These are paired with trap codes to detect sophisticated probes
    CANARY_PARAMS = {34, 55}  # Higher Fibonacci numbers rarely used
    
    def __init__(self, app, banned_ips: Set[str] = None, audit_logger=None):
        """
        Initialize honeypot middleware.
        
        Args:
            app: FastAPI application
            banned_ips: Set of banned IP addresses (shared reference)
            audit_logger: Audit logging instance
        """
        super().__init__(app)
        self.banned_ips = banned_ips if banned_ips is not None else set()
        self.audit_logger = audit_logger
        self.trap_triggers = {}  # IP -> List of trigger times
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request through honeypot detection.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is already banned
        if client_ip in self.banned_ips:
            if self.audit_logger:
                self.audit_logger.log_event("BANNED_ACCESS_ATTEMPT", {
                    'ip': client_ip,
                    'path': request.url.path
                })
            
            return Response(
                content="Access Denied - IP Banned",
                status_code=403,
                headers={"X-Honeypot-Triggered": "true"}
            )
        
        # For POST requests to /process, check for trap codes
        if request.method == "POST" and request.url.path == "/process":
            try:
                body = await request.body()
                body_str = body.decode('utf-8')
                
                # Parse input format: TASK-PARAM | CONTEXT
                if '-' in body_str:
                    codes_part = body_str.split('|')[0].strip()
                    if '-' in codes_part:
                        parts = codes_part.split('-')
                        task_code = int(parts[0])
                        param_code = int(parts[1]) if len(parts) > 1 else 0
                        
                        # Check for trap codes
                        is_trap = False
                        trap_reason = None
                        
                        if task_code in self.TRAP_CODES:
                            is_trap = True
                            trap_reason = f"Trap Task Code {task_code}"
                        
                        # Sophisticated probe detection: Valid task + Canary param
                        if param_code in self.CANARY_PARAMS:
                            is_trap = True
                            trap_reason = f"Canary Parameter {param_code}"
                        
                        if is_trap:
                            # Log the intrusion attempt
                            if self.audit_logger:
                                self.audit_logger.log_event("HONEYPOT_TRIGGERED", {
                                    'ip': client_ip,
                                    'task_code': task_code,
                                    'param_code': param_code,
                                    'reason': trap_reason,
                                    'input': body_str[:100]  # First 100 chars
                                })
                            
                            # Track trigger times for rate analysis
                            if client_ip not in self.trap_triggers:
                                self.trap_triggers[client_ip] = []
                            self.trap_triggers[client_ip].append(time.time())
                            
                            # Ban the IP permanently
                            self.banned_ips.add(client_ip)
                            
                            print(f"🚨 HONEYPOT TRIGGERED: {client_ip} used {trap_reason}")
                            
                            return Response(
                                content=f"Access Denied - Security Violation Detected",
                                status_code=403,
                                headers={
                                    "X-Honeypot-Triggered": "true",
                                    "X-Ban-Reason": trap_reason
                                }
                            )
                
            except Exception as e:
                # If parsing fails, let it through (will be caught by protocol validation)
                pass
        
        # Request is clean, proceed
        response = await call_next(request)
        return response
    
    def get_banned_count(self) -> int:
        """Get count of banned IPs."""
        return len(self.banned_ips)
    
    def get_trap_statistics(self) -> dict:
        """
        Get statistics about honeypot triggers.
        
        Returns:
            Dict with trigger counts and patterns
        """
        stats = {
            'total_banned': len(self.banned_ips),
            'trap_triggers': len(self.trap_triggers),
            'banned_ips': list(self.banned_ips),
            'trigger_details': {}
        }
        
        for ip, times in self.trap_triggers.items():
            stats['trigger_details'][ip] = {
                'trigger_count': len(times),
                'first_trigger': times[0] if times else None,
                'last_trigger': times[-1] if times else None
            }
        
        return stats
    
    def unban_ip(self, ip: str) -> bool:
        """
        Manually unban an IP (for testing or false positive correction).
        
        Args:
            ip: IP address to unban
            
        Returns:
            True if IP was banned and is now unbanned
        """
        if ip in self.banned_ips:
            self.banned_ips.remove(ip)
            if ip in self.trap_triggers:
                del self.trap_triggers[ip]
            return True
        return False


# Standalone test function
def test_honeypot():
    """Test honeypot detection logic."""
    print("=" * 60)
    print("HONEYPOT TEST")
    print("=" * 60)
    
    banned_ips = set()
    honeypot = CanaryHoneypotMiddleware(None, banned_ips=banned_ips)
    
    # Simulate trap code detection
    test_inputs = [
        ("2-1 | Normal request", False, "Normal"),
        ("43-1 | Trap code", True, "Trap Code 43"),
        ("47-2 | Another trap", True, "Trap Code 47"),
        ("3-34 | Canary param", True, "Canary Param 34"),
    ]
    
    for input_str, should_trap, desc in test_inputs:
        # Parse manually since we're not in async context
        codes_part = input_str.split('|')[0].strip()
        task_code = int(codes_part.split('-')[0])
        param_code = int(codes_part.split('-')[1])
        
        is_trap = task_code in honeypot.TRAP_CODES or param_code in honeypot.CANARY_PARAMS
        
        status = "TRAP" if is_trap else "PASS"
        result = "✓" if is_trap == should_trap else "✗"
        
        print(f"{result} {desc}: {input_str} -> {status}")
    
    print("\n" + "=" * 60)
    print("HONEYPOT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_honeypot()
