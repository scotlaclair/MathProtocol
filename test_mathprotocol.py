"""
Unit tests for MathProtocol using pytest.

Run with: pytest test_mathprotocol.py -v
"""

import pytest
from mathprotocol import MathProtocol, MockLLM


class TestMathProtocol:
    """Test suite for MathProtocol class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.protocol = MathProtocol()
    
    def test_valid_input_validation(self):
        """Test that valid inputs pass validation."""
        valid_inputs = [
            "2-1 | Good product",
            "17-2 | Hello World",
            "3-1 | Long text here",
            "5-1 | Bonjour"
        ]
        for inp in valid_inputs:
            assert self.protocol.validate_input(inp), f"Failed on: {inp}"
    
    def test_invalid_input_validation(self):
        """Test that invalid inputs fail validation."""
        invalid_inputs = [
            "4-1 | Text",  # 4 is not prime in our set
            "2-4 | Text",  # 4 is not Fibonacci
            "Hello",  # Wrong format
            "2-1-1 | Text"  # Too many dashes
        ]
        for inp in invalid_inputs:
            assert not self.protocol.validate_input(inp), f"Should have failed: {inp}"
    
    def test_input_parsing(self):
        """Test input parsing."""
        parsed = self.protocol.parse_input("17-1 | Hello World")
        assert parsed is not None
        assert parsed['task'] == 17
        assert parsed['param'] == 1
        assert parsed['context'] == "Hello World"
    
    def test_response_parsing(self):
        """Test response parsing."""
        parsed = self.protocol.parse_response("32-128 | Hola Mundo")
        assert parsed['codes'] == [32, 128]
        assert parsed['payload'] == "Hola Mundo"
    
    def test_response_validation_classification(self):
        """Test that classification tasks cannot have payloads."""
        # Valid: no payload (v2.1 with Success Bit: 2+1=3)
        assert self.protocol.validate_response("3-128", 2)
        # Invalid: has payload
        assert not self.protocol.validate_response("3-128 | Text", 2)
    
    def test_response_validation_generative(self):
        """Test that generative tasks must have payloads."""
        # Valid: has payload (v2.1 with Success Bit: 16+1=17)
        assert self.protocol.validate_response("17-128 | Text", 3)
        # Invalid: no payload
        assert not self.protocol.validate_response("17-128", 3)
    
    def test_task_name_lookup(self):
        """Test task name lookup."""
        assert self.protocol.get_task_name(2) == "Sentiment"
        assert self.protocol.get_task_name(17) == "Translate"
        assert self.protocol.get_task_name(999) is None
    
    def test_param_name_lookup(self):
        """Test parameter name lookup."""
        assert self.protocol.get_param_name(1) == "Brief"
        assert self.protocol.get_param_name(5) == "JSON"
        assert self.protocol.get_param_name(999) is None
    
    def test_response_name_lookup(self):
        """Test response name lookup."""
        assert self.protocol.get_response_name(2) == "Positive"
        assert self.protocol.get_response_name(128) == "HighConf"
        assert self.protocol.get_response_name(999) is None


class TestMockLLM:
    """Test suite for MockLLM class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_llm = MockLLM()
        self.protocol = MathProtocol()
    
    def test_sentiment_positive(self):
        """Test positive sentiment detection."""
        response = self.mock_llm.process("2-1 | This product is amazing!")
        # v2.1: 2 (Positive) + 1 (Success Bit) = 3
        assert response == "3-128"
    
    def test_sentiment_negative(self):
        """Test negative sentiment detection."""
        response = self.mock_llm.process("2-1 | This product is terrible!")
        # v2.1: 4 (Negative) + 1 (Success Bit) = 5
        assert response == "5-128"
    
    def test_translation(self):
        """Test translation task."""
        response = self.mock_llm.process("17-1 | Hello")
        parsed = self.protocol.parse_response(response)
        assert len(parsed['codes']) >= 2
        assert parsed['payload'] != ""
        # v2.1: 32 (Spanish) + 1 (Success Bit) = 33
        assert 33 in parsed['codes']  # Spanish with Success Bit
    
    def test_language_detection_french(self):
        """Test French language detection."""
        response = self.mock_llm.process("5-1 | Bonjour le monde")
        parsed = self.protocol.parse_response(response)
        # v2.1: 64 (French) + 1 (Success Bit) = 65
        assert 65 in parsed['codes']  # French with Success Bit
        assert parsed['payload'] == ""  # Classification task
    
    def test_qa(self):
        """Test question answering."""
        response = self.mock_llm.process("11-1 | What is the capital of France?")
        parsed = self.protocol.parse_response(response)
        assert "Paris" in parsed['payload']
    
    def test_error_invalid_task(self):
        """Test invalid task error."""
        response = self.mock_llm.process("4-1 | Text")
        assert response == "1024"
    
    def test_error_invalid_param(self):
        """Test invalid parameter error."""
        response = self.mock_llm.process("2-4 | Text")
        assert response == "2048"
    
    def test_error_invalid_format(self):
        """Test invalid format error."""
        response = self.mock_llm.process("Hello there")
        assert response == "4096"


class TestMathematicalSets:
    """Test the mathematical sets are correct."""
    
    def test_primes_set(self):
        """Verify all primes in the set are actually prime."""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        for p in MathProtocol.PRIMES:
            assert is_prime(p), f"{p} is not prime"
    
    def test_fibonacci_set(self):
        """Verify all numbers in Fibonacci set are actually Fibonacci numbers."""
        # Generate Fibonacci numbers up to 89
        fibs = [1, 1]
        while fibs[-1] < 89:
            fibs.append(fibs[-1] + fibs[-2])
        fib_set = set(fibs)
        
        for f in MathProtocol.FIBONACCI:
            assert f in fib_set, f"{f} is not a Fibonacci number"
    
    def test_powers_of_2_set(self):
        """Verify all numbers are powers of 2."""
        for p in MathProtocol.POWERS_OF_2:
            # Check if p is a power of 2
            assert p > 0 and (p & (p - 1)) == 0, f"{p} is not a power of 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
