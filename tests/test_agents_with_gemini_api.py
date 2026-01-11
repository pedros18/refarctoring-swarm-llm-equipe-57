"""
Test Suite for Agents with OpenRouter API
Tests all three agents using actual API calls
Path: tests/test_agents_with_gemini_api.py
"""

import os
import json
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv('OPENROUTER_API_KEY')
if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
    sys.exit(1)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "gpt-3.5-turbo"  # OpenRouter model

# ============================================================================
# TEST DATA
# ============================================================================

TEST_CODE_WITH_SYNTAX_ERROR = '''
def calculate_average(numbers)
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
'''

TEST_CODE_SIMPLE = '''
def add(x, y):
    return x + y
'''

# ============================================================================
# SYSTEM PROMPTS (from prompt files)
# ============================================================================

AUDITOR_SYSTEM_PROMPT = """You are an expert Python code auditor with great and deep knowledge of:
    - All bugs patterns
    - Best practices of python
    - Software maintainability
    - Quality of code

Your objective: Read the code, analyze it and produce a detailed refactoring plan. 

ROLE:
    - Emphasizes clear, complete but concise explanations
    - Never suggest changes that would break functionality 
    - Identify errors, missing features, or failing requirements
    - Do NOT modify any code
    - Do NOT propose fixes
    - Output MUST be valid JSON format

Your analysis should identify:
    - Syntax errors (highest priority)
    - Logical bugs
    - Missing docstrings
    - PEP 8 violations
    - Duplicated code, long functions, etc.
    - Detect and clearly describe the problem."""

FIXER_SYSTEM_PROMPT = """You are an expert Python developer specialized in code refactoring and fixing bugs.

Your mission: read the refactoring plan and apply the fixes to Python code.

CRITICAL RULES:
1. Fix only the issues mentioned in the refactoring plan
2. Keep and preserve all existing functionality
3. Don't add new features or change logic unless fixing a bug
4. Respect and maintain the original code structure when possible
5. Output ONLY the corrected Python code, no explanations
6. Ensure proper indentation (4 spaces in Python)
7. Keep existed imports unless they're causing errors

You are a expert code fixer - precise and minimal changes only."""

JUDGE_SYSTEM_PROMPT = """You are an expert testing Python codes.

Your mission: Evaluate fixed Python code by analyzing test results and decide if the fix is acceptable or needs revision.

DECISION RULES:
1. If ALL tests pass: Approve the fix (status: "SUCCESS")
2. If ANY test fails: Reject and provide a clear feedback (status: "NEEDS_REVISION")
3. Be specific about what went wrong
4. Suggest what the Fixer should focus on in the next iteration

You decide if the code is acceptable or not so be thorough but fair."""

# ============================================================================# HELPER FUNCTIONS
# ============================================================================

def call_gemini(system_prompt: str, user_prompt: str, model: str = MODEL) -> dict:
    """Call OpenRouter API and return response"""
    try:
        print(f"\n⏳ Calling {model}...")
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result_json = response.json()
        text = result_json["choices"][0]["message"]["content"]
        
        result = {
            "success": True,
            "text": text,
            "model": model,
            "finish_reason": result_json["choices"][0].get("finish_reason", "stop")
        }
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }

# ============================================================================
# TEST 1: AUDITOR WITH OPENROUTER API
# ============================================================================

def test_auditor_with_api():
    """Test Auditor agent with actual OpenRouter API"""
    print("\n" + "="*70)
    print("TEST 1: AUDITOR AGENT (OpenRouter API)")
    print("="*70)
    
    auditor_prompt = f"""Analyze the following Python file and create a refactoring plan.

FILE: test_syntax.py
CODE:
```python
{TEST_CODE_WITH_SYNTAX_ERROR}
```

OUTPUT FORMAT (JSON):
Provide your analysis as a JSON object with this exact structure:
{{
  "file_path": "test_syntax.py",
  "critical_issues": [
    {{
      "line": <line_number>,
      "type": "SyntaxError",
      "description": "Missing colon after function definition",
      "severity": "CRITICAL"
    }}
  ],
  "refactoring_suggestions": [],
  "summary": "Brief overview"
}}

IMPORTANT: Output ONLY valid JSON, no additional text."""

    print("\n📝 SENDING PROMPT TO AUDITOR...")
    print("-" * 70)
    print(auditor_prompt[:300] + "..." if len(auditor_prompt) > 300 else auditor_prompt)
    print("-" * 70)
    
    response = call_gemini(AUDITOR_SYSTEM_PROMPT, auditor_prompt)
    
    if not response["success"]:
        print(f"❌ API ERROR: {response['error']}")
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 70)
    print(response["text"][:500] + "..." if len(response["text"]) > 500 else response["text"])
    print("-" * 70)
    
    # Try to parse JSON
    try:
        clean_text = response["text"].strip()
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
        print("   Raw response wasn't valid JSON")
        return None

# ============================================================================
# TEST 2: FIXER WITH OPENROUTER API
# ============================================================================

def test_fixer_with_api():
    """Test Fixer agent with actual OpenRouter API"""
    print("\n" + "="*70)
    print("TEST 2: FIXER AGENT (OpenRouter API)")
    print("="*70)
    
    refactoring_plan = {
        "critical_issues": [
            {
                "line": 2,
                "type": "SyntaxError",
                "description": "Missing colon after function definition",
                "severity": "CRITICAL"
            }
        ],
        "refactoring_suggestions": []
    }
    
    fixer_prompt = f"""Fix the following Python code according to the refactoring plan.

FILE: test_syntax.py

ORIGINAL CODE:
```python
{TEST_CODE_WITH_SYNTAX_ERROR}
```

REFACTORING PLAN:
{json.dumps(refactoring_plan, indent=2)}

INSTRUCTIONS:
1. Fix all CRITICAL issues first
2. Output ONLY the corrected Python code

OUTPUT:
Provide ONLY the corrected Python code in ```python blocks.
No explanations or additional text.

Example output format:
```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
```"""

    print("\n📝 SENDING PROMPT TO FIXER...")
    print("-" * 70)
    print(fixer_prompt[:300] + "..." if len(fixer_prompt) > 300 else fixer_prompt)
    print("-" * 70)
    
    response = call_gemini(FIXER_SYSTEM_PROMPT, fixer_prompt)
    
    if not response["success"]:
        print(f"❌ API ERROR: {response['error']}")
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 70)
    print(response["text"][:500] + "..." if len(response["text"]) > 500 else response["text"])
    print("-" * 70)
    
    # Extract code
    if "```python" in response["text"]:
        fixed_code = response["text"].split("```python")[1].split("```")[0].strip()
        print("\n✅ CODE EXTRACTION: SUCCESS")
        print(f"   - Fixed code length: {len(fixed_code)} characters")
        
        # Verify syntax
        try:
            compile(fixed_code, "test", "exec")
            print("   - Syntax validation: PASS")
            return fixed_code
        except SyntaxError as e:
            print(f"   - Syntax validation: FAIL - {e}")
            return fixed_code
    else:
        print("\n⚠️ Warning: No ```python code block found in response")
        return None

# ============================================================================
# TEST 3: JUDGE WITH GEMINI API
# ============================================================================

def test_judge_with_api(fixed_code: str = None):
    """Test Judge agent with actual Gemini API"""
    print("\n" + "="*70)
    print("TEST 3: JUDGE AGENT (OpenRouter API)")
    print("="*70)
    
    if not fixed_code:
        fixed_code = """def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
"""
    
    test_results = {
        "passed": 2,
        "failed": 0,
        "failures": "",
        "errors": ""
    }
    
    judge_prompt = f"""Evaluate this code fix and determine if it is acceptable.

FILE: test_syntax.py

ORIGINAL CODE:
```python
{TEST_CODE_WITH_SYNTAX_ERROR}
```

FIXED CODE:
```python
{fixed_code}
```

TEST RESULTS:
✓ Tests passed: {test_results['passed']}
✗ Tests failed: {test_results['failed']}

YOUR TASK:
Analyze the test results and decide:

1. DECISION: Should this fix be accepted or rejected?
2. REASONING: Why did tests pass or fail?
3. FEEDBACK: What should the Fixer focus on next? (if rejected)

OUTPUT FORMAT (JSON):
{{
  "decision": "SUCCESS" or "NEEDS_REVISION",
  "reasoning": "Clear explanation of your decision",
  "tests_passed": 2,
  "tests_failed": 0,
  "next_steps": null,
  "estimated_iterations_remaining": 0
}}

IMPORTANT: Provide ONLY the JSON response, no additional text."""

    print("\n📝 SENDING PROMPT TO JUDGE...")
    print("-" * 70)
    print(judge_prompt[:300] + "..." if len(judge_prompt) > 300 else judge_prompt)
    print("-" * 70)
    
    response = call_gemini(JUDGE_SYSTEM_PROMPT, judge_prompt)
    
    if not response["success"]:
        print(f"❌ API ERROR: {response['error']}")
        return None
    
    print("\n✅ RESPONSE RECEIVED:")
    print("-" * 70)
    print(response["text"][:500] + "..." if len(response["text"]) > 500 else response["text"])
    print("-" * 70)
    
    # Try to parse JSON
    try:
        clean_text = response["text"].strip()
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

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("🧪 AGENT TESTING WITH GOOGLE GEMINI API")
    print("="*70)
    print(f"Model: {MODEL}")
    print(f"API Key: {'✅ Configured' if API_KEY else '❌ Missing'}")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Auditor
    try:
        analysis = test_auditor_with_api()
        if analysis:
            tests_passed += 1
        else:
            tests_failed += 1
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        tests_failed += 1
    
    # Test 2: Fixer
    try:
        fixed_code = test_fixer_with_api()
        if fixed_code:
            tests_passed += 1
        else:
            tests_failed += 1
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        tests_failed += 1
    
    # Test 3: Judge
    try:
        evaluation = test_judge_with_api(fixed_code)
        if evaluation:
            tests_passed += 1
        else:
            tests_failed += 1
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📈 Success Rate: {(tests_passed/3)*100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Agents work with Gemini API.")
    else:
        print(f"\n⚠️ {tests_failed} test(s) failed. Review errors above.")
    
    print("="*70 + "\n")
    
    return tests_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
