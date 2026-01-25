System Role:
You are a Senior Python Developer and AI Prompt Engineer. I need you to build a complete Deterministic LLM Control Protocol called "MathProtocol".
The Objective:
Create a Python-based system that forces an LLM to communicate using strict mathematical codes. This prevents prompt injection and allows the LLM to function as a logic engine in software pipelines.
Part 1: The Protocol Specification
The protocol relies on three mathematical sets to validate data:
 * Primes (2-97) for TASKS.
 * Fibonacci (1-89) for PARAMETERS.
 * Powers of 2 (2-4096) for RESPONSES.
The Rules:
 * Input Format: [TASK]-[PARAM] | [CONTEXT]
   * The pipe | is mandatory if context is provided.
   * Example: 17-1 | Hello World (Translate "Hello World" briefly).
 * Output Format: [RESPONSE]-[CONFIDENCE] | [PAYLOAD]
   * Classification Tasks (Codes Only): Tasks 2, 5, 13, 19, 29. The LLM MUST NOT output a payload.
     * Example: 2-128 (Positive, High Confidence).
   * Generative Tasks (Hybrid): Tasks 3, 7, 11, 17, 23. The LLM MUST output a payload after the pipe.
     * Example: 32-128 | Hola Mundo (Spanish, High Conf | Content).
 * Error Handling:
   * If the input is invalid, output only the error code (no confidence, no payload).
   * Codes: 1024 (Invalid Task), 2048 (Invalid Param), 4096 (Invalid Format).
Part 2: The Coding Request
Please generate two distinct deliverables:
Deliverable A: The System Prompt
Write the actual text I should paste into the LLM's system instructions. It must:
 * Clearly define the mappings (listed below).
 * Enforce the "Payload Whitelist" (which tasks allow text vs which do not).
 * Include "Few-Shot" examples for both valid and invalid flows.
Deliverable B: The Python Test Harness
Write a Python script with the following structure:
 * class MathProtocol:
   * validate_input(str): Returns true if format matches Prime-Fib | Text.
   * parse_response(str): Returns a dictionary { "codes": [], "payload": "..." }.
   * mappings: Dictionaries for all codes (Primes/Fib/Powers).
 * class MockLLM:
   * A function that simulates the LLM's behavior locally (if I send 2-1 | Good, it returns 2-128). This allows me to test the logic without an API key initially.
 * run_tests():
   * A function that runs 5-10 specific test cases (Sentiment, Translation, Error Injection) and prints PASS/FAIL.
Reference Mappings:
 * Tasks (Primes): 2=Sentiment, 3=Summarization, 5=Lang Detect, 7=Entity Extract, 11=Q&A, 13=Classify, 17=Translate, 19=Moderate, 23=Keywords, 29=Readability.
 * Params (Fibonacci): 1=Brief, 2=Medium, 3=Detailed, 5=JSON, 8=List, 13=Confidence, 21=Explain.
 * Responses (Powers of 2): 2=Positive, 4=Negative, 8=Neutral, 16=English, 32=Spanish, 64=French, 128=HighConf, 256=MedConf, 512=LowConf.
