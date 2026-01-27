"""
MathProtocol v2.1: A deterministic LLM control protocol using mathematical codes.

This module implements a strict protocol that forces LLMs to communicate using
predefined mathematical codes (primes, fibonacci, powers of 2) to prevent
prompt injection and ensure deterministic behavior.

Version 2.1 adds the mandatory Success Bit requirement for enhanced validation.
Version 2.1 also adds ProtocolRegistry for dynamic task/parameter registration.
"""

import re
from typing import Dict, List, Optional, Union, Any


class ProtocolRegistry:
    """
    Dynamic Registry for MathProtocol tasks and parameters.
    Allows for extensibility without modifying the core library.
    
    This is a singleton that maintains mappings between mathematical codes
    and their semantic meanings. It can be extended at runtime to support
    custom protocol extensions.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProtocolRegistry, cls).__new__(cls)
            cls._instance.tasks = {}
            cls._instance.parameters = {}
            cls._instance.responses = {}
            cls._instance._initialize_defaults()
        return cls._instance

    def _initialize_defaults(self):
        """Initialize default protocol mappings."""
        # Register default primes (tasks) to match MathProtocol.TASKS
        self.register_task(2, "Sentiment")
        self.register_task(3, "Summarization")
        self.register_task(5, "LangDetect")
        self.register_task(7, "EntityExtract")
        self.register_task(11, "Q&A")
        self.register_task(13, "Classify")
        self.register_task(17, "Translate")
        self.register_task(19, "Moderate")
        self.register_task(23, "Keywords")
        self.register_task(29, "Readability")

        # Register default fibonacci (parameters) to match MathProtocol.PARAMS
        self.register_parameter(1, "Brief")
        self.register_parameter(2, "Medium")
        self.register_parameter(3, "Detailed")
        self.register_parameter(5, "JSON")
        self.register_parameter(8, "List")
        self.register_parameter(13, "Confidence")
        self.register_parameter(21, "Explain")
        # Extended parameters not in original PARAMS
        self.register_parameter(34, "INCLUDE_CITATIONS")
        self.register_parameter(55, "REDACT_PII")
        self.register_parameter(89, "MAX_PRECISION")

        # Register default powers of 2 (responses) to match MathProtocol.RESPONSES
        # Success Bit (mandatory in v2.1, treated separately from semantic flags)
        self.register_response(1, "SUCCESS_BIT")
        # Semantic response flags (must align with MathProtocol.RESPONSES)
        self.register_response(2, "Positive")
        self.register_response(4, "Negative")
        self.register_response(8, "Neutral")
        self.register_response(16, "English")
        self.register_response(32, "Spanish")
        self.register_response(64, "French")
        self.register_response(128, "HighConf")
        self.register_response(256, "MedConf")
        self.register_response(512, "LowConf")

    def reset(self):
        """Reset registry to default state (primarily for testing)."""
        self.tasks = {}
        self.parameters = {}
        self.responses = {}
        self._initialize_defaults()

    def register_task(self, prime: int, name: str):
        """
        Register a new task code.
        
        Args:
            prime: A prime number to use as task identifier
            name: Human-readable name for the task
            
        Raises:
            ValueError: If the provided number is not prime or not in the
                predefined MathProtocol.PRIMES task set (when protocol is loaded).
        """
        if not self._is_prime(prime):
            raise ValueError(f"Task ID {prime} must be a prime number.")
        # Enforce that task codes stay within the core protocol's prime set
        # to maintain strict, deterministic validation.
        # Only validate against PRIMES if MathProtocol class exists (avoid circular import during init)
        if 'MathProtocol' in globals():
            MP = globals()['MathProtocol']
            if prime not in MP.PRIMES:
                raise ValueError(
                    f"Task ID {prime} is not a valid protocol task code. "
                    f"Valid task IDs are: {sorted(MP.PRIMES)}"
                )
        self.tasks[prime] = name

    def register_parameter(self, fib: int, name: str):
        """
        Register a new parameter code.
        
        Args:
            fib: A fibonacci number to use as parameter identifier
            name: Human-readable name for the parameter
        
        Raises:
            ValueError: If the provided number is not a valid Fibonacci parameter code
                (when protocol is loaded).
        """
        # Only validate against FIBONACCI if MathProtocol class exists (avoid circular import during init)
        if 'MathProtocol' in globals():
            MP = globals()['MathProtocol']
            if fib not in MP.FIBONACCI:
                raise ValueError(f"Parameter ID {fib} must be a valid Fibonacci value from the protocol set: {sorted(MP.FIBONACCI)}")
        self.parameters[fib] = name

    def register_response(self, power: int, name: str):
        """
        Register a new response code.
        
        Args:
            power: A power of 2 to use as response identifier
            name: Human-readable name for the response
            
        Raises:
            ValueError: If the provided number is not a power of 2
        """
        if not (power > 0 and (power & (power - 1)) == 0):
            raise ValueError(f"Response ID {power} must be a power of 2.")
        self.responses[power] = name
    
    def get_task_name(self, prime: int) -> str:
        """Get the name of a registered task."""
        return self.tasks.get(prime, f"UNKNOWN_TASK_{prime}")

    def get_parameter_name(self, fib: int) -> str:
        """Get the name of a registered parameter."""
        return self.parameters.get(fib, f"UNKNOWN_PARAM_{fib}")

    def get_response_flags(self, code: int) -> List[str]:
        """
        Decode a response code into its constituent flags.
        
        Args:
            code: Integer response code (may be composite of multiple flags)
            
        Returns:
            List of flag names that are set in the code
        """
        flags = []
        for power, name in self.responses.items():
            if code & power:
                flags.append(name)
        return flags

    @staticmethod
    def _is_prime(n: int) -> bool:
        """Check if a number is prime."""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True


# Singleton instance for global access
registry = ProtocolRegistry()


class MathProtocol:
    """
    Main protocol class for validating inputs and parsing outputs.
    
    The protocol uses three mathematical sets:
    - Primes (2-97): For TASKS
    - Fibonacci (1-89): For PARAMETERS
    - Powers of 2 (2-4096): Base codes for RESPONSES and CONFIDENCE
    
    Version 2.1 Feature: Success Bit Validation
    - Success Bit: 1 (LSB) is reserved as the Success Bit
    - Base response codes are powers of 2 (e.g., 16 for English)
    - Transmitted response value MUST be base_code + Success Bit (i.e., odd)
      Example (transmitted): 17-128 where 17 = 16 (English) + 1 (Success Bit)
      Invalid (missing Success Bit): 16-128
    - Confidence codes remain pure powers of 2 and are transmitted as-is:
      128=HighConf, 256=MedConf, 512=LowConf
    """
    
    # Mathematical sets
    PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    FIBONACCI = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
    # v2.1: Added 1 (Success Bit) to powers of 2
    POWERS_OF_2 = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096}
    
    # Task mappings
    TASKS = {
        2: "Sentiment",
        3: "Summarization",
        5: "LangDetect",
        7: "EntityExtract",
        11: "Q&A",
        13: "Classify",
        17: "Translate",
        19: "Moderate",
        23: "Keywords",
        29: "Readability"
    }
    
    # Parameter mappings
    PARAMS = {
        1: "Brief",
        2: "Medium",
        3: "Detailed",
        5: "JSON",
        8: "List",
        13: "Confidence",
        21: "Explain"
    }
    
    # Response mappings
    RESPONSES = {
        2: "Positive",
        4: "Negative",
        8: "Neutral",
        16: "English",
        32: "Spanish",
        64: "French",
        128: "HighConf",
        256: "MedConf",
        512: "LowConf"
    }
    
    # Error codes
    ERROR_INVALID_TASK = 1024
    ERROR_INVALID_PARAM = 2048
    ERROR_INVALID_FORMAT = 4096
    
    # Task types
    CLASSIFICATION_TASKS = {2, 5, 13, 19, 29}  # No payload
    GENERATIVE_TASKS = {3, 7, 11, 17, 23}  # Requires payload
    
    def __init__(self):
        """Initialize MathProtocol with registry reference."""
        self.registry = registry
    
    # === NEW V2 METHODS ===
    
    def construct_prompt(self, task_prime: int, params_fib: List[int], context: str) -> str:
        """
        Constructs the deterministic mathematical prompt (V2 API).
        
        Args:
            task_prime: Prime number identifying the task
            params_fib: List of Fibonacci numbers as parameters
            context: The data context for the task
            
        Returns:
            Formatted protocol prompt string
        """
        fib_sum = sum(params_fib) if params_fib else 1
        checksum = task_prime * fib_sum
        
        prompt = (
            f"MATHPROTOCOL_V2_REQUEST\n"
            f"TASK_PRIME: {task_prime}\n"
            f"PARAM_FIB: {params_fib}\n"
            f"CHECKSUM: {checksum}\n"
            f"DATA_START\n"
            f"{context}\n"
            f"DATA_END\n"
            f"INSTRUCTION: Execute TASK {task_prime} with modifiers {params_fib}. "
            f"Respond strictly in MathProtocol response format: "
            f"\"<response_code>-<confidence>\" for classification tasks (no payload) "
            f"or \"<response_code>-<confidence> | <payload>\" for generative tasks. "
            f"Use only the defined integer codes and output nothing else."
        )
        return prompt

    def decode_response(self, response_int: int) -> Dict[str, Any]:
        """
        Decodes the integer response from the LLM (V2 API).
        
        Args:
            response_int: Integer response code from the LLM
            
        Returns:
            Dictionary with decoded response information
        """
        is_success = (response_int & 1) == 1
        flags = self.registry.get_response_flags(response_int)
        
        return {
            "raw_code": response_int,
            "success": is_success,
            "flags": flags,
            "description": " | ".join(flags)
        }

    def validate_request(self, task_prime: int, params_fib: List[int]) -> bool:
        """
        Validates if the task and params are registered (V2 API).
        
        Args:
            task_prime: Prime number task identifier
            params_fib: List of Fibonacci parameter identifiers
            
        Returns:
            True if all codes are registered, False otherwise
        """
        if task_prime not in self.registry.tasks:
            return False
        for p in params_fib:
            if p not in self.registry.parameters:
                return False
        return True
    
    # === EXISTING V1 METHODS - PRESERVED FOR BACKWARD COMPATIBILITY ===
    
    def validate_input(self, input_str: str) -> bool:
        """
        Validate if input matches the format: [TASK]-[PARAM] | [CONTEXT]
        or [TASK]-[PARAM] (without context).
        
        Args:
            input_str: The input string to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        if not input_str or not isinstance(input_str, str):
            return False
        
        # Pattern: TASK-PARAM with optional | CONTEXT
        # Use atomic grouping to prevent catastrophic backtracking (ReDoS)
        # The non-capturing group (?:...) with explicit character limits prevents
        # exponential backtracking when matching whitespace around the pipe
        pattern = r'^(\d+)-(\d+)(?:\s{0,10}\|\s{0,10}(.+))?$'
        match = re.match(pattern, input_str)
        
        if not match:
            return False
        
        task = int(match.group(1))
        param = int(match.group(2))
        
        # Validate task is a prime in our set
        if task not in self.PRIMES or task not in self.TASKS:
            return False
        
        # Validate param is a Fibonacci number in our set
        if param not in self.FIBONACCI:
            return False
        
        return True
    
    def parse_input(self, input_str: str) -> Optional[Dict[str, Union[int, str]]]:
        """
        Parse a valid input string into its components.
        
        Args:
            input_str: The input string to parse
            
        Returns:
            Dict with 'task', 'param', and 'context' keys, or None if invalid
        """
        if not self.validate_input(input_str):
            return None
        
        # Extract components
        if '|' in input_str:
            codes, context = input_str.split('|', 1)
            context = context.strip()
        else:
            codes = input_str
            context = ""
        
        task, param = map(int, codes.split('-'))
        
        return {
            'task': task,
            'param': param,
            'context': context
        }
    
    def parse_response(self, response_str: str) -> Dict[str, Union[List[int], str]]:
        """
        Parse an LLM response into codes and payload.
        
        Args:
            response_str: The response string from the LLM
            
        Returns:
            Dict with 'codes' (list of integers) and 'payload' (string) keys
        """
        if not response_str or not isinstance(response_str, str):
            return {"codes": [], "payload": ""}
        
        # Check if response contains a pipe (has payload)
        if '|' in response_str:
            codes_part, payload = response_str.split('|', 1)
            payload = payload.strip()
        else:
            codes_part = response_str
            payload = ""
        
        # Extract all numbers from codes part
        codes = [int(x) for x in re.findall(r'\d+', codes_part)]
        
        return {
            "codes": codes,
            "payload": payload
        }
    
    def validate_response(self, response_str: str, task_code: int) -> bool:
        """
        Validate if a response matches protocol rules for the given task.
        
        Version 2.1: Enforces Success Bit requirement.
        The first response code MUST have bit 0 set (be odd).
        
        Valid examples:
        - 17-128 (16 English + 1 Success Bit)
        - 3-128 (2 Positive + 1 Success Bit)
        - 1-128 (0 + 1 Success Bit only)
        
        Invalid examples:
        - 16-128 (missing Success Bit)
        - 2-128 (missing Success Bit)
        
        Args:
            response_str: The response string to validate
            task_code: The task code that generated this response
            
        Returns:
            bool: True if valid response, False otherwise
        """
        parsed = self.parse_response(response_str)
        codes = parsed["codes"]
        payload = parsed["payload"]
        
        # Error codes should be alone (and don't require Success Bit)
        if len(codes) == 1 and codes[0] in {1024, 2048, 4096}:
            return payload == ""  # Error codes should have no payload
        
        # Normal responses should have exactly 2 codes (response + confidence)
        if len(codes) != 2:
            return False
        
        response_val = codes[0]
        confidence_val = codes[1]
        
        # v2.1: Check Success Bit (bit 0 must be set - number must be odd)
        if not (response_val & 1):
            return False  # Missing Success Bit!
        
        # Remove Success Bit to validate the base code
        base_code = response_val - 1
        
        # Base code must be a valid power of 2 or 0
        # Valid bases: 0 (just success), 2, 4, 8, 16, 32, 64
        valid_bases = {0, 2, 4, 8, 16, 32, 64}
        if base_code not in valid_bases:
            return False
        
        # Confidence code must be valid
        CONFIDENCE_CODES = {128, 256, 512}
        if confidence_val not in CONFIDENCE_CODES:
            return False
        
        # Classification tasks must NOT have payload
        if task_code in self.CLASSIFICATION_TASKS:
            return payload == ""
        
        # Generative tasks MUST have payload
        if task_code in self.GENERATIVE_TASKS:
            return payload != ""
        
        return True
    
    def get_task_name(self, task_code: int) -> Optional[str]:
        """Get the name of a task from its code."""
        return self.TASKS.get(task_code)
    
    def get_param_name(self, param_code: int) -> Optional[str]:
        """Get the name of a parameter from its code."""
        return self.PARAMS.get(param_code)
    
    def get_response_name(self, response_code: int) -> Optional[str]:
        """Get the name of a response from its code."""
        return self.RESPONSES.get(response_code)


class MockLLM:
    """
    Mock LLM that simulates protocol-compliant behavior for testing.
    
    This allows testing the protocol logic without requiring an actual LLM API.
    """
    
    def __init__(self):
        self.protocol = MathProtocol()
    
    def process(self, input_str: str) -> str:
        """
        Process an input according to MathProtocol rules.
        
        Args:
            input_str: The input string in protocol format
            
        Returns:
            str: The response in protocol format
        """
        # Parse input
        parsed = self.protocol.parse_input(input_str)
        
        if parsed is None:
            # Determine specific error
            if not input_str or not re.match(r'^\d+-\d+', input_str):
                return str(MathProtocol.ERROR_INVALID_FORMAT)
            
            # Extract codes to check which is invalid
            match = re.match(r'^(\d+)-(\d+)', input_str)
            if match:
                task = int(match.group(1))
                param = int(match.group(2))
                
                if task not in MathProtocol.PRIMES or task not in MathProtocol.TASKS:
                    return str(MathProtocol.ERROR_INVALID_TASK)
                if param not in MathProtocol.FIBONACCI:
                    return str(MathProtocol.ERROR_INVALID_PARAM)
            
            return str(MathProtocol.ERROR_INVALID_FORMAT)
        
        task = parsed['task']
        param = parsed['param']
        context = parsed['context']
        
        # Simulate task-specific responses
        return self._generate_response(task, param, context)
    
    def _generate_response(self, task: int, param: int, context: str) -> str:
        """
        Generate a mock response based on task type.
        
        Version 2.1: All responses include the Success Bit (+1 to base code).
        """
        
        # Task 2: Sentiment Analysis
        if task == 2:
            # Simple keyword-based sentiment
            context_lower = context.lower()
            if any(word in context_lower for word in ['good', 'great', 'amazing', 'excellent', 'love']):
                return "3-128"  # 2 Positive + 1 Success Bit
            elif any(word in context_lower for word in ['bad', 'terrible', 'awful', 'hate', 'worst']):
                return "5-128"  # 4 Negative + 1 Success Bit
            else:
                return "9-128"  # 8 Neutral + 1 Success Bit
        
        # Task 3: Summarization
        elif task == 3:
            words = context.split()
            if param == 1:  # Brief
                summary = ' '.join(words[:5]) + "..."
            elif param == 2:  # Medium
                summary = ' '.join(words[:10]) + "..."
            else:  # Detailed
                summary = ' '.join(words[:15]) + "..."
            return f"17-128 | {summary}"  # 16 English + 1 Success Bit
        
        # Task 5: Language Detection
        elif task == 5:
            context_lower = context.lower()
            # Simple keyword-based detection
            spanish_words = ['hola', 'mundo', 'gracias', 'por', 'favor']
            french_words = ['bonjour', 'monde', 'merci', 'oui', 'non']
            
            if any(word in context_lower for word in spanish_words):
                return "33-128"  # 32 Spanish + 1 Success Bit
            elif any(word in context_lower for word in french_words):
                return "65-128"  # 64 French + 1 Success Bit
            else:
                return "17-128"  # 16 English + 1 Success Bit
        
        # Task 7: Entity Extraction
        elif task == 7:
            # Simple capitalized word extraction
            words = context.split()
            entities = [w for w in words if w and w[0].isupper() and w not in ['The', 'A', 'An']]
            if param == 8:  # List format
                result = ', '.join(entities[:5])
            else:
                result = ' '.join(entities[:3])
            return f"17-128 | {result}"  # 16 English + 1 Success Bit
        
        # Task 11: Q&A
        elif task == 11:
            # Simple mock answers
            if 'capital' in context.lower() and 'france' in context.lower():
                return "17-128 | Paris"  # 16 English + 1 Success Bit
            elif 'color' in context.lower() and 'sky' in context.lower():
                return "17-128 | Blue"  # 16 English + 1 Success Bit
            else:
                return "17-128 | Answer not available"  # 16 English + 1 Success Bit
        
        # Task 13: Classification
        elif task == 13:
            # Generic classification as neutral
            return "9-128"  # 8 Neutral + 1 Success Bit
        
        # Task 17: Translation
        elif task == 17:
            # Simple mock translations
            context_lower = context.lower()
            if 'hello' in context_lower or 'hi' in context_lower:
                return "33-128 | Hola"  # 32 Spanish + 1 Success Bit
            elif 'world' in context_lower:
                return "33-128 | Mundo"  # 32 Spanish + 1 Success Bit
            elif 'thank' in context_lower:
                return "33-128 | Gracias"  # 32 Spanish + 1 Success Bit
            else:
                return "33-128 | [traducción]"  # 32 Spanish + 1 Success Bit
        
        # Task 19: Content Moderation
        elif task == 19:
            # Simple safety check
            unsafe_words = ['violence', 'hate', 'explicit']
            if any(word in context.lower() for word in unsafe_words):
                return "5-128"  # 4 Negative (unsafe) + 1 Success Bit
            else:
                return "9-128"  # 8 Neutral (safe) + 1 Success Bit
        
        # Task 23: Keyword Extraction
        elif task == 23:
            # Extract first few words as keywords
            words = [w.strip('.,!?') for w in context.split()]
            keywords = ', '.join(words[:5])
            return f"17-128 | {keywords}"  # 16 English + 1 Success Bit
        
        # Task 29: Readability
        elif task == 29:
            # Simple readability: positive if short words
            avg_word_length = sum(len(w) for w in context.split()) / max(len(context.split()), 1)
            if avg_word_length < 5:
                return "3-128"  # 2 Positive (easy to read) + 1 Success Bit
            elif avg_word_length > 8:
                return "5-128"  # 4 Negative (hard to read) + 1 Success Bit
            else:
                return "9-128"  # 8 Neutral (medium) + 1 Success Bit
        
        # Default fallback
        return "9-128"  # 8 Neutral + 1 Success Bit


def run_tests():
    """
    Run comprehensive test cases for MathProtocol.
    
    Tests include:
    - Input validation
    - Response parsing
    - Classification tasks
    - Generative tasks
    - Error handling
    - MockLLM behavior
    """
    protocol = MathProtocol()
    mock_llm = MockLLM()
    
    print("=" * 60)
    print("MathProtocol Test Suite")
    print("=" * 60)
    
    test_count = 0
    passed_count = 0
    
    # Test 1: Valid input validation
    test_count += 1
    print(f"\nTest {test_count}: Valid Input Validation")
    valid_inputs = [
        "2-1 | Good product",
        "17-2 | Hello World",
        "3-1 | Long text here",
        "5-1 | Bonjour"
    ]
    all_valid = all(protocol.validate_input(inp) for inp in valid_inputs)
    print(f"Result: {'PASS' if all_valid else 'FAIL'}")
    if all_valid:
        passed_count += 1
    
    # Test 2: Invalid input validation
    test_count += 1
    print(f"\nTest {test_count}: Invalid Input Validation")
    invalid_inputs = [
        "4-1 | Text",  # 4 is not prime in our set
        "2-4 | Text",  # 4 is not Fibonacci
        "Hello",  # Wrong format
        "2-1-1 | Text"  # Too many dashes
    ]
    all_invalid = all(not protocol.validate_input(inp) for inp in invalid_inputs)
    print(f"Result: {'PASS' if all_invalid else 'FAIL'}")
    if all_invalid:
        passed_count += 1
    
    # Test 3: Input parsing
    test_count += 1
    print(f"\nTest {test_count}: Input Parsing")
    parsed = protocol.parse_input("17-1 | Hello World")
    correct_parse = (parsed is not None and 
                     parsed['task'] == 17 and 
                     parsed['param'] == 1 and 
                     parsed['context'] == "Hello World")
    print(f"Parsed: {parsed}")
    print(f"Result: {'PASS' if correct_parse else 'FAIL'}")
    if correct_parse:
        passed_count += 1
    
    # Test 4: Response parsing
    test_count += 1
    print(f"\nTest {test_count}: Response Parsing")
    parsed_resp = protocol.parse_response("32-128 | Hola Mundo")
    correct_resp = (parsed_resp['codes'] == [32, 128] and 
                    parsed_resp['payload'] == "Hola Mundo")
    print(f"Parsed: {parsed_resp}")
    print(f"Result: {'PASS' if correct_resp else 'FAIL'}")
    if correct_resp:
        passed_count += 1
    
    # Test 5: Sentiment Analysis (Classification - No Payload)
    test_count += 1
    print(f"\nTest {test_count}: Sentiment Analysis")
    response = mock_llm.process("2-1 | This product is amazing!")
    print(f"Input: 2-1 | This product is amazing!")
    print(f"Output: {response}")
    # v2.1: Expecting 3-128 (2 Positive + 1 Success Bit)
    valid_sentiment = protocol.parse_response(response)['codes'] == [3, 128]
    print(f"Result: {'PASS' if valid_sentiment else 'FAIL'}")
    if valid_sentiment:
        passed_count += 1
    
    # Test 6: Translation (Generative - Requires Payload)
    test_count += 1
    print(f"\nTest {test_count}: Translation")
    response = mock_llm.process("17-1 | Hello")
    print(f"Input: 17-1 | Hello")
    print(f"Output: {response}")
    parsed = protocol.parse_response(response)
    valid_translation = (len(parsed['codes']) >= 2 and 
                        parsed['payload'] != "")
    print(f"Result: {'PASS' if valid_translation else 'FAIL'}")
    if valid_translation:
        passed_count += 1
    
    # Test 7: Error - Invalid Task
    test_count += 1
    print(f"\nTest {test_count}: Invalid Task Error")
    response = mock_llm.process("4-1 | Text")
    print(f"Input: 4-1 | Text")
    print(f"Output: {response}")
    valid_error = response == "1024"
    print(f"Result: {'PASS' if valid_error else 'FAIL'}")
    if valid_error:
        passed_count += 1
    
    # Test 8: Error - Invalid Parameter
    test_count += 1
    print(f"\nTest {test_count}: Invalid Parameter Error")
    response = mock_llm.process("2-4 | Text")
    print(f"Input: 2-4 | Text")
    print(f"Output: {response}")
    valid_error = response == "2048"
    print(f"Result: {'PASS' if valid_error else 'FAIL'}")
    if valid_error:
        passed_count += 1
    
    # Test 9: Error - Invalid Format
    test_count += 1
    print(f"\nTest {test_count}: Invalid Format Error")
    response = mock_llm.process("Hello there")
    print(f"Input: Hello there")
    print(f"Output: {response}")
    valid_error = response == "4096"
    print(f"Result: {'PASS' if valid_error else 'FAIL'}")
    if valid_error:
        passed_count += 1
    
    # Test 10: Language Detection (Classification - No Payload)
    test_count += 1
    print(f"\nTest {test_count}: Language Detection")
    response = mock_llm.process("5-1 | Bonjour le monde")
    print(f"Input: 5-1 | Bonjour le monde")
    print(f"Output: {response}")
    parsed = protocol.parse_response(response)
    # v2.1: Expecting 65-128 (64 French + 1 Success Bit)
    valid_langdetect = (len(parsed['codes']) == 2 and 
                       parsed['payload'] == "" and
                       65 in parsed['codes'])  # 64 French + 1 Success Bit
    print(f"Result: {'PASS' if valid_langdetect else 'FAIL'}")
    if valid_langdetect:
        passed_count += 1
    
    # Test 11: Response Validation
    test_count += 1
    print(f"\nTest {test_count}: Response Validation")
    # v2.1: All responses must have Success Bit (odd numbers)
    # Classification task should not have payload
    valid1 = protocol.validate_response("3-128", 2)  # Valid (2+1 Success Bit)
    valid2 = not protocol.validate_response("3-128 | Text", 2)  # Invalid (has payload)
    # Generative task should have payload
    valid3 = protocol.validate_response("17-128 | Text", 3)  # Valid (16+1 Success Bit)
    valid4 = not protocol.validate_response("17-128", 3)  # Invalid (no payload)
    # Missing Success Bit should fail
    valid5 = not protocol.validate_response("2-128", 2)  # Invalid (missing Success Bit)
    valid6 = not protocol.validate_response("16-128 | Text", 3)  # Invalid (missing Success Bit)
    all_validation_correct = valid1 and valid2 and valid3 and valid4 and valid5 and valid6
    print(f"Result: {'PASS' if all_validation_correct else 'FAIL'}")
    if all_validation_correct:
        passed_count += 1
    
    # Test 12: Q&A (Generative)
    test_count += 1
    print(f"\nTest {test_count}: Question Answering")
    response = mock_llm.process("11-1 | What is the capital of France?")
    print(f"Input: 11-1 | What is the capital of France?")
    print(f"Output: {response}")
    parsed = protocol.parse_response(response)
    valid_qa = (len(parsed['codes']) >= 2 and 
                parsed['payload'] != "" and
                "Paris" in parsed['payload'])
    print(f"Result: {'PASS' if valid_qa else 'FAIL'}")
    if valid_qa:
        passed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_count}/{test_count} passed")
    print("=" * 60)
    
    return passed_count == test_count


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
