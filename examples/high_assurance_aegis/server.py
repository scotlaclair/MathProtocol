"""
AEGIS FastAPI Server - High-Assurance MathProtocol Deployment

This server demonstrates a production-grade deployment with:
- DataAirlock for PHI/PII protection
- Merkle Audit Chain for tamper-evident logging
- Circuit Breaker for fault isolation
- Dead Letter Vault for forensic analysis
- Honeypot Middleware for active defense

Security Controls: HIPAA, NIST SP 800-53, OWASP LLM Top 10
"""

import sys
import os

# Add parent directory to path to import mathprotocol
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os

from mathprotocol import MathProtocol, MockLLM
from aegis_core import DataAirlock, MerkleAuditChain, CircuitBreaker, DeadLetterVault
from honeypot import CanaryHoneypotMiddleware

# Security: Admin API key from environment variable
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key-change-in-production")


# Request/Response Models
class ProcessRequest(BaseModel):
    """Request model for /process endpoint."""
    input: str
    redact_phi: bool = True


class ProcessResponse(BaseModel):
    """Response model for /process endpoint."""
    output: str
    redacted_input: Optional[str] = None
    security_metadata: Optional[Dict[str, Any]] = None


# Initialize Security Components
airlock = DataAirlock()
audit_chain = MerkleAuditChain(log_dir="./aegis_audit_logs", batch_size=10)
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
dead_letter_vault = DeadLetterVault(vault_dir="./aegis_dead_letters")
banned_ips = set()  # Shared across honeypot middleware

# Initialize Protocol and LLM
protocol = MathProtocol()
llm = MockLLM()  # In production, replace with real LLM client


# FastAPI Application
app = FastAPI(
    title="AEGIS MathProtocol Server",
    description="Military-Grade MathProtocol deployment with multi-layer security",
    version="1.0.0"
)

# Add Honeypot Middleware
app.add_middleware(
    CanaryHoneypotMiddleware,
    banned_ips=banned_ips,
    audit_logger=audit_chain
)


@app.post("/process", response_model=ProcessResponse)
async def process_request(request: ProcessRequest, http_request: Request):
    """
    Process a MathProtocol request with full security pipeline.
    
    Security Flow:
    1. Honeypot checks request (middleware)
    2. DataAirlock redacts PHI/PII
    3. Circuit Breaker protects against failures
    4. LLM processes sanitized input
    5. Audit Chain logs transaction
    6. Dead Letter Vault captures failures
    7. DataAirlock rehydrates response
    
    Args:
        request: ProcessRequest with input string
        http_request: HTTP request context
        
    Returns:
        ProcessResponse with output and metadata
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    # Log request metadata only (no raw input to avoid PHI/PII leakage)
    audit_chain.log_event("REQUEST", {
        'ip': client_ip,
        'redact_phi': request.redact_phi
    })
    
    try:
        # Step 1: Validate Protocol Input
        if not protocol.validate_input(request.input):
            audit_chain.log_event("VALIDATION_FAILED", {
                'ip': client_ip
            })
            raise HTTPException(status_code=400, detail="Invalid protocol format")
        
        # Step 2: Redact PHI/PII
        redacted_input = request.input
        token_map = {}
        
        if request.redact_phi:
            # Extract context from input
            if '|' in request.input:
                codes, context = request.input.split('|', 1)
                redacted_context, token_map = airlock.redact(context.strip())
                redacted_input = f"{codes.strip()} | {redacted_context}"
            else:
                redacted_input = request.input
        
        # Step 3: Process with Circuit Breaker Protection
        def process_with_llm():
            """Wrapper for circuit breaker."""
            return llm.process(redacted_input)
        
        raw_output = circuit_breaker.call(process_with_llm)
        
        # Step 4: Validate Response
        parsed_input = protocol.parse_input(request.input)
        task_code = parsed_input['task'] if parsed_input else 0
        
        if not protocol.validate_response(raw_output, task_code):
            raise ValueError("LLM violated protocol")
        
        # Step 5: Rehydrate Response (restore PHI if it was redacted)
        final_output = raw_output
        if request.redact_phi and token_map:
            if '|' in raw_output:
                codes, payload = raw_output.split('|', 1)
                rehydrated_payload = airlock.rehydrate(payload.strip(), token_map)
                final_output = f"{codes.strip()} | {rehydrated_payload}"
        
        # Step 6: Log Success
        audit_chain.log_event("SUCCESS", {
            'ip': client_ip,
            'input': request.input[:100],  # Truncate for privacy
            'output': final_output[:100],
            'circuit_state': circuit_breaker.get_state()
        })
        
        # Build response with security metadata
        security_metadata = {
            'phi_redacted': request.redact_phi and len(token_map) > 0,
            'token_count': len(token_map),
            'circuit_state': circuit_breaker.get_state()['state'],
            'request_logged': True
        }
        
        return ProcessResponse(
            output=final_output,
            redacted_input=redacted_input if request.redact_phi else None,
            security_metadata=security_metadata
        )
        
    except Exception as e:
        # Generate correlation ID for tracking
        import uuid
        correlation_id = str(uuid.uuid4())
        
        # Log failure with full details
        audit_chain.log_event("ERROR", {
            'ip': client_ip,
            'correlation_id': correlation_id,
            'error_type': type(e).__name__,
            'circuit_state': circuit_breaker.get_state()
        })
        
        # Store in Dead Letter Vault
        request_data = {
            'ip': client_ip,
            'redact_phi': request.redact_phi,
            'correlation_id': correlation_id
        }
        dead_letter_vault.store(request_data, e)
        
        # Return generic error response (don't leak exception details)
        raise HTTPException(
            status_code=500, 
            detail=f"Processing failed. Correlation ID: {correlation_id}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint with security status.
    
    Returns:
        System health and security metrics
    """
    circuit_state = circuit_breaker.get_state()
    
    health = {
        'status': 'healthy' if circuit_state['state'] == 'CLOSED' else 'degraded',
        'circuit_breaker': circuit_state,
        'banned_ips': len(banned_ips),
        'dead_letters': len(dead_letter_vault.list_failed()),
        'audit_chain_valid': audit_chain.verify_chain()
    }
    
    return JSONResponse(content=health)


@app.get("/security/status")
async def security_status():
    """
    Get detailed security status.
    
    Returns:
        Comprehensive security metrics
    """
    return {
        'circuit_breaker': circuit_breaker.get_state(),
        'banned_ips': {
            'count': len(banned_ips),
            'list': list(banned_ips)
        },
        'dead_letters': {
            'count': len(dead_letter_vault.list_failed()),
            'files': dead_letter_vault.list_failed()
        },
        'audit_chain': {
            'valid': audit_chain.verify_chain(),
            'buffer_size': len(audit_chain.buffer)
        }
    }


@app.post("/security/reset")
async def reset_security(http_request: Request, api_key: Optional[str] = None, component: Optional[str] = "all"):
    """
    Reset security components (admin endpoint, requires authentication).
    
    Query parameter:
        api_key: Admin API key for authentication
        component: Component to reset (circuit_breaker, bans, vault, all)
        
    Returns:
        Reset status
    """
    # Verify API key using constant-time comparison
    import hmac
    if not api_key or not hmac.compare_digest(api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API key")
    reset_actions = []
    
    if component in ["circuit_breaker", "all"]:
        circuit_breaker.reset()
        reset_actions.append("circuit_breaker")
    
    if component in ["bans", "all"]:
        banned_ips.clear()
        reset_actions.append("banned_ips")
    
    if component in ["vault", "all"]:
        dead_letter_vault.clear_vault()
        reset_actions.append("dead_letter_vault")
    
    if component in ["airlock", "all"]:
        airlock.clear_vault()
        reset_actions.append("data_airlock")
    
    return {
        'status': 'reset',
        'components': reset_actions
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Flush audit logs on shutdown."""
    audit_chain.force_flush()
    print("AEGIS Server shutdown - Audit logs flushed")


# Development server
if __name__ == "__main__":
    print("=" * 60)
    print("🛡 AEGIS MathProtocol Server Starting")
    print("=" * 60)
    print("\nSecurity Features Active:")
    print("  ✓ DataAirlock (PHI/PII Redaction)")
    print("  ✓ Merkle Audit Chain")
    print("  ✓ Circuit Breaker")
    print("  ✓ Dead Letter Vault")
    print("  ✓ Honeypot Middleware")
    print("\nEndpoints:")
    print("  POST /process - Process MathProtocol requests")
    print("  GET  /health - Health check")
    print("  GET  /security/status - Security metrics")
    print("  POST /security/reset - Reset security components")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
