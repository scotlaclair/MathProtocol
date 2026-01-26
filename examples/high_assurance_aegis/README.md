# AEGIS Reference Implementation
The "Aegis" implementation demonstrates what a MathProtocol system looks like when deployed in a high-security, military-grade environment.

It moves beyond simple input validation to provide Active Defense, Forensic Survivability, and Zero-Trust Data Handling.

##### The Defense Layers
1. 🛡 Data Airlock (PHI/PII Redaction)

Before the LLM logic engine ever sees a prompt, the Airlock scans for Regex patterns matching sensitive data (Emails, SSNs, Medical Record Numbers).

*  Action: Replaces sensitive data with deterministic tokens (e.g., <EMAIL_1>).
*  Result: The LLM processes the logic without ever seeing the secret. The secret is
re-hydrated only at the network edge before returning to the user.

2. 🚨 Prime Honeypots (Active Defense)
Most security is passive. Aegis is active.

*  The Trap: We designate specific Prime Numbers (e.g., 43, 47, 53) as "Trap Codes". They look like valid protocol tasks but are functionally useless.
*  The Trigger: If a client sends a request using Task 47, we know they are probing the system blindly.
*  The Response: The client IP is immediately and permanently added to the BANNED_IPS set.

3. ⛓ Merkle Audit Chain
Standard logs can be deleted or become an I/O bottleneck. Aegis logs are batched and cryptographically sealed.

*  The Architecture: Instead of writing every log entry to disk, events are buffered in memory. At a set threshold, the system computes the Merkle Root of all buffered event hashes. This single root is then cryptographically chained to the previous root and the entire batch is written to disk in a single, efficient operation.
*  The Result: This provides the same tamper-evidence as a linear hash chain but with significantly higher throughput and reduced disk I/O, making it suitable for high-traffic environments.

4. ⚰ Dead Letter Vault & Circuit Breaker
*  Circuit Breaker: If the Logic Engine fails (e.g., API downtime), the breaker trips, rejecting traffic instantly to prevent resource exhaustion.
*  Dead Letter Vault: Failed transactions aren't lost. They are serialized (Inputs + Stack Trace) into JSON files in the Vault for forensic replay later.

##### Running the Live Fire Exercise
We have included a simulation script that acts as both a legitimate user and an attacker to demonstrate these defenses in real-time.

```bash
# From the root of the repo
python examples/high_assurance_aegis/demo_live_fire.py
```

Watch the console for the color-coded engagement log.
