"""
Example usage of MathProtocol.

This file demonstrates various use cases of the MathProtocol system.
"""

from mathprotocol import MathProtocol, MockLLM


def main():
    """Run example demonstrations of MathProtocol."""
    
    protocol = MathProtocol()
    mock_llm = MockLLM()
    
    print("=" * 70)
    print("MathProtocol Examples")
    print("=" * 70)
    
    # Example 1: Sentiment Analysis
    print("\n### Example 1: Sentiment Analysis (Classification Task)")
    print("-" * 70)
    test_inputs = [
        "2-1 | This product is amazing!",
        "2-1 | This product is terrible.",
        "2-1 | The product is okay."
    ]
    
    for input_str in test_inputs:
        response = mock_llm.process(input_str)
        parsed = protocol.parse_response(response)
        
        # Interpret the response
        sentiment = "Unknown"
        if 2 in parsed['codes']:
            sentiment = "Positive"
        elif 4 in parsed['codes']:
            sentiment = "Negative"
        elif 8 in parsed['codes']:
            sentiment = "Neutral"
        
        confidence = "Unknown"
        if 128 in parsed['codes']:
            confidence = "High"
        elif 256 in parsed['codes']:
            confidence = "Medium"
        elif 512 in parsed['codes']:
            confidence = "Low"
        
        print(f"Input:  {input_str}")
        print(f"Output: {response}")
        print(f"Interpretation: {sentiment} sentiment, {confidence} confidence")
        print()
    
    # Example 2: Translation
    print("\n### Example 2: Translation (Generative Task)")
    print("-" * 70)
    translation_inputs = [
        "17-1 | Hello",
        "17-1 | Thank you",
        "17-2 | Good morning"
    ]
    
    for input_str in translation_inputs:
        response = mock_llm.process(input_str)
        parsed = protocol.parse_response(response)
        
        print(f"Input:  {input_str}")
        print(f"Output: {response}")
        print(f"Translation: {parsed['payload']}")
        print()
    
    # Example 3: Language Detection
    print("\n### Example 3: Language Detection (Classification Task)")
    print("-" * 70)
    lang_inputs = [
        "5-1 | Hello World",
        "5-1 | Hola Mundo",
        "5-1 | Bonjour le monde"
    ]
    
    for input_str in lang_inputs:
        response = mock_llm.process(input_str)
        parsed = protocol.parse_response(response)
        
        # Interpret language
        language = "Unknown"
        if 16 in parsed['codes']:
            language = "English"
        elif 32 in parsed['codes']:
            language = "Spanish"
        elif 64 in parsed['codes']:
            language = "French"
        
        print(f"Input:  {input_str}")
        print(f"Output: {response}")
        print(f"Detected Language: {language}")
        print()
    
    # Example 4: Question Answering
    print("\n### Example 4: Question Answering (Generative Task)")
    print("-" * 70)
    qa_inputs = [
        "11-1 | What is the capital of France?",
        "11-1 | What color is the sky?",
    ]
    
    for input_str in qa_inputs:
        response = mock_llm.process(input_str)
        parsed = protocol.parse_response(response)
        
        print(f"Input:  {input_str}")
        print(f"Output: {response}")
        print(f"Answer: {parsed['payload']}")
        print()
    
    # Example 5: Error Handling
    print("\n### Example 5: Error Handling")
    print("-" * 70)
    error_inputs = [
        ("4-1 | Some text", "Invalid Task (4 is not prime in our set)"),
        ("2-4 | Some text", "Invalid Parameter (4 is not Fibonacci)"),
        ("Hello there", "Invalid Format (doesn't match pattern)")
    ]
    
    for input_str, description in error_inputs:
        response = mock_llm.process(input_str)
        
        error_map = {
            str(protocol.ERROR_INVALID_TASK): "Invalid Task Code",
            str(protocol.ERROR_INVALID_PARAM): "Invalid Parameter Code",
            str(protocol.ERROR_INVALID_FORMAT): "Invalid Format",
        }
        error_msg = error_map.get(response, "Unknown Error")
        
        print(f"Input:  {input_str}")
        print(f"Description: {description}")
        print(f"Output: {response}")
        print(f"Error: {error_msg}")
        print()
    
    # Example 6: Summarization with different lengths
    print("\n### Example 6: Summarization with Different Parameters")
    print("-" * 70)
    long_text = "The quick brown fox jumps over the lazy dog. This is a common pangram used in typography and design. It contains every letter of the English alphabet at least once."
    
    for param in [1, 2, 3]:
        param_name = protocol.get_param_name(param)
        input_str = f"3-{param} | {long_text}"
        response = mock_llm.process(input_str)
        parsed = protocol.parse_response(response)
        
        print(f"Input:  3-{param} (Summarization - {param_name})")
        print(f"Output: {response}")
        print(f"Summary: {parsed['payload']}")
        print()
    
    # Example 7: Validation
    print("\n### Example 7: Input Validation")
    print("-" * 70)
    
    validation_tests = [
        ("2-1 | Good text", True),
        ("17-5 | Text", True),
        ("4-1 | Bad task", False),
        ("2-6 | Bad param", False),
        ("invalid", False)
    ]
    
    for input_str, expected in validation_tests:
        is_valid = protocol.validate_input(input_str)
        status = "✓" if is_valid == expected else "✗"
        print(f"{status} Input: {input_str:30s} -> Valid: {is_valid} (Expected: {expected})")
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
