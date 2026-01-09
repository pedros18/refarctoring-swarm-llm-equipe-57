"""
Test script for prompt files - OpenRouter API
Path: tests/test_prompts_openrouter.py

Uses OpenRouter - $5 free credit, access to many models!
"""

import os
import json
import requests
from dotenv import load_dotenv

# Import your prompts
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.prompts.auditor_prompts import (
    Auditor_SYSTEM_PROMPT,
    get_analysis_prompt
)
from src.prompts.fixer_prompts import (
    FIXER_SYSTEM_PROMPT,
    get_fix_prompt
)
from src.prompts.judge_prompts import (
    JUDGE_SYSTEM_PROMPT,
    get_evaluation_prompt
)

# Load API key
load_dotenv()

# Sample buggy code for testing
BUGGY_CODE_SAMPLE = """
def calculate_average(numbers)
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

def greet(name):
    print("Hello " + name)
    
class Calculator
    def add(self,a,b):
        return a+b
"""

PYLINT_SAMPLE = """
************* Module test_code
test_code.py:1:0: C0114: Missing module docstring (missing-module-docstring)
test_code.py:2:31: E0001: invalid syntax (<unknown>, line 2) (syntax-error)
test_code.py:8:6: C0116: Missing function or method docstring (missing-function-docstring)
"""


def call_openrouter(system_prompt, user_prompt, model="google/gemini-2.0-flash-exp:free"):
    """
    Call OpenRouter API
    
    Available FREE models:
    - google/gemini-2.0-flash-exp:free (Fast & Good - Recommended)
    - meta-llama/llama-3.2-3b-instruct:free (Fast)
    - microsoft/phi-3-mini-128k-instruct:free (Small & Fast)
    - qwen/qwen-2-7b-instruct:free (Good quality)
    """
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
        return None
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"   Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None


def test_auditor_prompts():
    """Test the Auditor Agent prompts"""
    print("="*60)
    print("🔍 TESTING AUDITOR PROMPTS (OpenRouter)")
    print("="*60)
    
    # Generate the analysis prompt
    prompt = get_analysis_prompt(
        file_path="sandbox/test_code.py",
        code_content=BUGGY_CODE_SAMPLE,
        pylint_output=PYLINT_SAMPLE
    )
    
    print("\n📝 PROMPT SENT TO API:")
    print("-" * 60)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 60)
    
    # Call API
    print("\n⏳ Calling OpenRouter API (using free Gemini model)...")
    response_text = call_openrouter(Auditor_SYSTEM_PROMPT, prompt)
    
    if not response_text:
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 60)
    print(response_text)
    print("-" * 60)
    
    # Try to parse as JSON
    try:
        clean_text = response_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(clean_text)
        print("\n✅ JSON PARSING: SUCCESS")
        print(f"   - Critical issues found: {len(analysis.get('critical_issues', []))}")
        print(f"   - Refactoring suggestions: {len(analysis.get('refactoring_suggestions', []))}")
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON PARSING FAILED: {e}")
        print("   Response wasn't valid JSON")
        return None


def test_fixer_prompts(refactoring_plan):
    """Test the Fixer Agent prompts"""
    print("\n" + "="*60)
    print("🔧 TESTING FIXER PROMPTS (OpenRouter)")
    print("="*60)
    
    if not refactoring_plan:
        print("⚠️  Skipping - no refactoring plan from auditor test")
        return None
    
    # Generate the fix prompt
    prompt = get_fix_prompt(
        file_path="sandbox/test_code.py",
        original_code=BUGGY_CODE_SAMPLE,
        refactoring_plan=json.dumps(refactoring_plan, indent=2)
    )
    
    print("\n📝 PROMPT SENT TO API:")
    print("-" * 60)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 60)
    
    # Call API
    print("\n⏳ Calling OpenRouter API...")
    response_text = call_openrouter(FIXER_SYSTEM_PROMPT, prompt)
    
    if not response_text:
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 60)
    print(response_text)
    print("-" * 60)
    
    # Extract code from response
    if "```python" in response_text:
        fixed_code = response_text.split("```python")[1].split("```")[0].strip()
        print("\n✅ CODE EXTRACTION: SUCCESS")
        print(f"   - Fixed code length: {len(fixed_code)} characters")
        return fixed_code
    else:
        print("\n⚠️  Warning: No ```python code block found")
        return response_text


def test_judge_prompts(fixed_code):
    """Test the Judge Agent prompts"""
    print("\n" + "="*60)
    print("⚖️  TESTING JUDGE PROMPTS (OpenRouter)")
    print("="*60)
    
    if not fixed_code:
        print("⚠️  Skipping - no fixed code from fixer test")
        return None
    
    # Simulate test results
    test_results = {
        'passed': 2,
        'failed': 1,
        'failures': 'test_calculate_average FAILED: AssertionError: Division by zero not handled',
        'errors': ''
    }
    
    # Generate the evaluation prompt
    prompt = get_evaluation_prompt(
        file_path="sandbox/test_code.py",
        original_code=BUGGY_CODE_SAMPLE,
        fixed_code=fixed_code,
        test_results=test_results
    )
    
    print("\n📝 PROMPT SENT TO API:")
    print("-" * 60)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 60)
    
    # Call API
    print("\n⏳ Calling OpenRouter API...")
    response_text = call_openrouter(JUDGE_SYSTEM_PROMPT, prompt)
    
    if not response_text:
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 60)
    print(response_text)
    print("-" * 60)
    
    # Try to parse as JSON
    try:
        clean_text = response_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0].strip()
        
        evaluation = json.loads(clean_text)
        print("\n✅ JSON PARSING: SUCCESS")
        print(f"   - Decision: {evaluation.get('decision')}")
        print(f"   - Tests passed: {evaluation.get('tests_passed')}")
        print(f"   - Tests failed: {evaluation.get('tests_failed')}")
        return evaluation
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON PARSING FAILED: {e}")
        return None


def check_balance():
    """Check your OpenRouter credit balance"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        return
    
    try:
        response = requests.get(
            url="https://openrouter.ai/api/v1/auth/key",
            headers={
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"💰 Your OpenRouter balance: ${data.get('data', {}).get('limit', 'Unknown')}")
        
    except:
        pass  # Don't fail if balance check doesn't work


def main():
    """Run all prompt tests"""
    print("\n" + "🚀 STARTING PROMPT TESTING (OpenRouter)")
    print("="*60)
    
    # Check API key
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
        print("\n📝 To get your API key:")
        print("1. Go to: https://openrouter.ai")
        print("2. Sign up (you get $5 free credit!)")
        print("3. Go to: https://openrouter.ai/keys")
        print("4. Create a key and add it to .env")
        return
    
    print("✅ OpenRouter API key loaded")
    check_balance()
    print("🤖 Using free Gemini model via OpenRouter\n")
    
    print("="*60)
    
    # Test each agent's prompts
    analysis_result = test_auditor_prompts()
    
    fixed_code = test_fixer_prompts(analysis_result)
    
    evaluation_result = test_judge_prompts(fixed_code)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Auditor test: {'PASSED' if analysis_result else 'FAILED'}")
    print(f"✅ Fixer test: {'PASSED' if fixed_code else 'FAILED'}")
    print(f"✅ Judge test: {'PASSED' if evaluation_result else 'FAILED'}")
    
    if analysis_result and fixed_code and evaluation_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your prompts work perfectly!")
    
    print("\n💡 Check your remaining balance at: https://openrouter.ai/credits")
    print()


if __name__ == "__main__":
    main()