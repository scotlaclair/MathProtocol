from typing import Optional, Dict, Any, Union
from mathprotocol import MathProtocol

class MathProtocolClient:
    """
    A wrapper for LLM clients that handles the MathProtocol handshake automatically.

    It supports:
    - OpenAI (client.chat.completions.create)
    - Anthropic (client.messages.create)
    """
    def __init__(self, llm_client, model: str, system_prompt: str, provider: str = "openai"):
        """
        Args:
            llm_client: An initialized OpenAI or Anthropic client object.
            model (str): The model name (e.g., "gpt-4", "claude-3-opus").
            system_prompt (str): The full text from SYSTEM_PROMPT.md.
            provider (str): "openai" or "anthropic"
        """
        self.client = llm_client
        self.model = model
        self.system_prompt = system_prompt
        self.provider = provider.lower()
        self.protocol = MathProtocol()

    def execute(self, task_code: int, param_code: int, context: str = "") -> Dict[str, Any]:
        """
        Execute a task using the protocol. Handles formatting, validation, and parsing.

        Returns:
            Dict containing parsed response codes and payload.
            Returns {'error': code} if validation fails.
        """
        # 1. Construct Input
        # Only add the pipe if context exists
        separator = " | " if context else ""
        input_str = f"{task_code}-{param_code}{separator}{context}"

        # 2. Local Validation (Save API tokens/money on bad input)
        if not self.protocol.validate_input(input_str):
            return {
                "error": self.protocol.ERROR_INVALID_FORMAT, 
                "message": "Client-side input validation failed. Check Task (Prime) and Param (Fibonacci) codes."
            }

        # 3. Call LLM
        raw_output = ""
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": input_str}
                    ],
                    temperature=0  # Deterministic behavior is key!
                )
                raw_output = response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": input_str}
                    ],
                    temperature=0
                )
                raw_output = response.content[0].text
        
        except Exception as e:
            return {"error": 500, "message": f"LLM Provider Error: {str(e)}"}

        # 4. Validate & Parse Response
        if not self.protocol.validate_response(raw_output, task_code):
            return {
                "error": 4096, 
                "raw_response": raw_output, 
                "message": "LLM violated protocol (Invalid response format or codes)"
            }

        return self.protocol.parse_response(raw_output)