"""
OpenRouter Client for Refactoring Swarm
Handles API calls to OpenRouter with proper error handling and logging
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenRouterClient:
    """Client for making API calls to OpenRouter"""
    
    def __init__(self, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize OpenRouter client
        
        Args:
            model: Model to use. Popular options:
                - "anthropic/claude-3.5-sonnet" (recommended for quality)
                - "anthropic/claude-3-haiku" (faster, cheaper)
                - "openai/gpt-4-turbo"
                - "openai/gpt-3.5-turbo"
                - "google/gemini-pro-1.5"
                - "meta-llama/llama-3.1-70b-instruct"
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables. "
                "Please add it to your .env file"
            )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
    
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> str:
        """
        Generate a response from OpenRouter
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    def generate_with_context(self, prompt: str, context: str, system_prompt: str = None, max_tokens: int = 2000) -> str:
        """
        Generate a response with additional context
        
        Args:
            prompt: The main question/instruction
            context: Additional context (e.g., code to analyze)
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        full_prompt = f"{context}\n\n{prompt}"
        return self.generate(full_prompt, system_prompt, max_tokens)


# Example usage functions for different agent types

def analyze_code_with_openrouter(code: str, filename: str) -> dict:
    """
    Example: Auditor Agent - Analyze code for issues
    
    Returns:
        dict with 'prompt', 'response', and 'issues'
    """
    client = OpenRouterClient(model="anthropic/claude-3.5-sonnet")
    
    system_prompt = """You are a Python code auditor. Analyze the provided code and identify:
1. Syntax errors
2. Logic bugs
3. Missing docstrings
4. PEP 8 violations
5. Potential improvements

Return your analysis in a structured format."""
    
    prompt = f"""Analyze this Python file: {filename}

Code:
```python
{code}
```

Provide a detailed analysis of all issues found."""
    
    response = client.generate(prompt, system_prompt, max_tokens=2000)
    
    return {
        'input_prompt': prompt,
        'output_response': response,
        'system_prompt': system_prompt
    }


def fix_code_with_openrouter(code: str, issues: str, filename: str) -> dict:
    """
    Example: Fixer Agent - Fix code based on identified issues
    
    Returns:
        dict with 'prompt', 'response', and 'fixed_code'
    """
    client = OpenRouterClient(model="anthropic/claude-3.5-sonnet")
    
    system_prompt = """You are a Python code fixer. Given code and a list of issues:
1. Fix all identified problems
2. Maintain the original functionality
3. Add proper docstrings
4. Follow PEP 8 standards
5. Return ONLY the fixed code, no explanations"""
    
    prompt = f"""Fix this Python file: {filename}

Original Code:
```python
{code}
```

Issues to fix:
{issues}

Return the complete fixed code."""
    
    response = client.generate(prompt, system_prompt, max_tokens=3000)
    
    return {
        'input_prompt': prompt,
        'output_response': response,
        'system_prompt': system_prompt
    }


def generate_tests_with_openrouter(code: str, filename: str) -> dict:
    """
    Example: Test Generator - Generate unit tests for code
    
    Returns:
        dict with 'prompt', 'response', and 'test_code'
    """
    client = OpenRouterClient(model="anthropic/claude-3.5-sonnet")
    
    system_prompt = """You are a Python test generator. Given code:
1. Generate comprehensive pytest unit tests
2. Cover edge cases and error conditions
3. Use descriptive test names
4. Include docstrings in tests
5. Return ONLY the test code"""
    
    prompt = f"""Generate pytest unit tests for this Python file: {filename}

Code to test:
```python
{code}
```

Return complete pytest test code."""
    
    response = client.generate(prompt, system_prompt, max_tokens=2000)
    
    return {
        'input_prompt': prompt,
        'output_response': response,
        'system_prompt': system_prompt
    }


# Model recommendations by use case
MODEL_RECOMMENDATIONS = {
    'analysis': 'anthropic/claude-3.5-sonnet',  # Best for code analysis
    'fixing': 'anthropic/claude-3.5-sonnet',     # Best for code generation
    'testing': 'anthropic/claude-3.5-sonnet',    # Best for test generation
    'fast': 'anthropic/claude-3-haiku',          # Faster, cheaper option
    'gpt4': 'openai/gpt-4-turbo',                # Alternative high-quality option
    'budget': 'openai/gpt-3.5-turbo',            # Cheapest option
}


def get_recommended_model(task_type: str = 'analysis') -> str:
    """Get recommended model for a specific task"""
    return MODEL_RECOMMENDATIONS.get(task_type, 'anthropic/claude-3.5-sonnet')


if __name__ == "__main__":
    """Test the OpenRouter client"""
    print("Testing OpenRouter client...")
    
    # Test code
    test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
    
    try:
        # Test analysis
        print("\n1. Testing code analysis...")
        result = analyze_code_with_openrouter(test_code, "test.py")
        print(f"✅ Analysis successful!")
        print(f"Response preview: {result['output_response'][:100]}...")
        
        print("\n✅ OpenRouter client is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. OPENROUTER_API_KEY is set in .env file")
        print("2. You have sufficient credits on OpenRouter")
        print("3. Internet connection is working")