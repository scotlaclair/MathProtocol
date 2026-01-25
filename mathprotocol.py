"""
MathProtocol: A deterministic LLM control protocol using mathematical codes.

This module implements a strict protocol that forces LLMs to communicate using
predefined mathematical codes (primes, fibonacci, powers of 2) to prevent
prompt injection and ensure deterministic behavior.
"""

import re
from typing import Dict, List, Optional, Union


class MathProtocol:
    """
    Main protocol class for validating inputs and parsing outputs.
    
    The protocol uses three mathematical sets:
    - Primes (2-97): For TASKS
    - Fibonacci (1-89): For PARAMETERS
    - Powers of 2 (2-4096): For RESPONSES and CONFIDENCE
    """
    
    # Mathematical sets
    PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    FIBONACCI = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
    POWERS_OF_2 = {2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096}
    
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
        pattern = r'^(\d+)-(\d+)(\s*\|\s*.+)?$'
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
        
        Args:
            response_str: The response string to validate
            task_code: The task code that generated this response
            
        Returns:
            bool: True if valid response, False otherwise
        """
        parsed = self.parse_response(response_str)
        codes = parsed["codes"]
        payload = parsed["payload"]
        
        # Error codes should be alone
        if len(codes) == 1 and codes[0] in {self.ERROR_INVALID_TASK, 
                                              self.ERROR_INVALID_PARAM, 
                                              self.ERROR_INVALID_FORMAT}:
            return payload == ""  # Error codes should have no payload
        
        # Normal responses should have exactly 2 codes (response + confidence)
        if len(codes) != 2:
            return False
        
        # All codes must be powers of 2
        if not all(code in self.POWERS_OF_2 for code in codes):
            return False
        
        # Valid confidence codes
        CONFIDENCE_CODES = {128, 256, 512}
        
        # Second code must be a valid confidence code
        if codes[1] not in CONFIDENCE_CODES:
            return False
        
        # First code must be a non-confidence response code
        VALID_RESPONSE_CODES = {2, 4, 8, 16, 32, 64}
        if codes[0] not in VALID_RESPONSE_CODES:
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
        """Generate a mock response based on task type."""
        
        # Task 2: Sentiment Analysis
        if task == 2:
            # Simple keyword-based sentiment
            context_lower = context.lower()
            if any(word in context_lower for word in ['good', 'great', 'amazing', 'excellent', 'love']):
                return "2-128"  # Positive, High Confidence
            elif any(word in context_lower for word in ['bad', 'terrible', 'awful', 'hate', 'worst']):
                return "4-128"  # Negative, High Confidence
            else:
                return "8-128"  # Neutral, High Confidence
        
        # Task 3: Summarization
        elif task == 3:
            words = context.split()
            if param == 1:  # Brief
                summary = ' '.join(words[:5]) + "..."
            elif param == 2:  # Medium
                summary = ' '.join(words[:10]) + "..."
            else:  # Detailed
                summary = ' '.join(words[:15]) + "..."
            return f"16-128 | {summary}"
        
        # Task 5: Language Detection
        elif task == 5:
            context_lower = context.lower()
            # Simple keyword-based detection
            spanish_words = ['hola', 'mundo', 'gracias', 'por', 'favor']
            french_words = ['bonjour', 'monde', 'merci', 'oui', 'non']
            
            if any(word in context_lower for word in spanish_words):
                return "32-128"  # Spanish, High Confidence
            elif any(word in context_lower for word in french_words):
                return "64-128"  # French, High Confidence
            else:
                return "16-128"  # English, High Confidence
        
        # Task 7: Entity Extraction
        elif task == 7:
            # Simple capitalized word extraction
            words = context.split()
            entities = [w for w in words if w and w[0].isupper() and w not in ['The', 'A', 'An']]
            if param == 8:  # List format
                result = ', '.join(entities[:5])
            else:
                result = ' '.join(entities[:3])
            return f"16-128 | {result}"
        
        # Task 11: Q&A
        elif task == 11:
            # Simple mock answers
            if 'capital' in context.lower() and 'france' in context.lower():
                return "16-128 | Paris"
            elif 'color' in context.lower() and 'sky' in context.lower():
                return "16-128 | Blue"
            else:
                return "16-128 | Answer not available"
        
        # Task 13: Classification
        elif task == 13:
            # Generic classification as neutral
            return "8-128"
        
        # Task 17: Translation
        elif task == 17:
            # Simple mock translations
            context_lower = context.lower()
            if 'hello' in context_lower or 'hi' in context_lower:
                return "32-128 | Hola"
            elif 'world' in context_lower:
                return "32-128 | Mundo"
            elif 'thank' in context_lower:
                return "32-128 | Gracias"
            else:
                return "32-128 | [traducción]"
        
        # Task 19: Content Moderation
        elif task == 19:
            # Simple safety check
            unsafe_words = ['violence', 'hate', 'explicit']
            if any(word in context.lower() for word in unsafe_words):
                return "4-128"  # Negative (unsafe)
            else:
                return "8-128"  # Neutral (safe)
        
        # Task 23: Keyword Extraction
        elif task == 23:
            # Extract first few words as keywords
            words = [w.strip('.,!?') for w in context.split()]
            keywords = ', '.join(words[:5])
            return f"16-128 | {keywords}"
        
        # Task 29: Readability
        elif task == 29:
            # Simple readability: positive if short words
            avg_word_length = sum(len(w) for w in context.split()) / max(len(context.split()), 1)
            if avg_word_length < 5:
                return "2-128"  # Positive (easy to read)
            elif avg_word_length > 8:
                return "4-128"  # Negative (hard to read)
            else:
                return "8-128"  # Neutral (medium)
        
        # Default fallback
        return "8-128"


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
    valid_sentiment = protocol.parse_response(response)['codes'] == [2, 128]
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
    valid_langdetect = (len(parsed['codes']) == 2 and 
                       parsed['payload'] == "" and
                       64 in parsed['codes'])  # French
    print(f"Result: {'PASS' if valid_langdetect else 'FAIL'}")
    if valid_langdetect:
        passed_count += 1
    
    # Test 11: Response Validation
    test_count += 1
    print(f"\nTest {test_count}: Response Validation")
    # Classification task should not have payload
    valid1 = protocol.validate_response("2-128", 2)  # Valid
    valid2 = not protocol.validate_response("2-128 | Text", 2)  # Invalid (has payload)
    # Generative task should have payload
    valid3 = protocol.validate_response("16-128 | Text", 3)  # Valid
    valid4 = not protocol.validate_response("16-128", 3)  # Invalid (no payload)
    all_validation_correct = valid1 and valid2 and valid3 and valid4
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
