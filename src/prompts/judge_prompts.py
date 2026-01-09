"""
Prompts for the Judge Agent
Role: Evaluates when the fixed code passes tests and decides next steps

"""

JUDGE_SYSTEM_PROMPT = """You are an expert testing Python codes.

Your mission: Evaluate fixed Python code by analyzing test results and decide if the fix is acceptable or needs revision.

DECISION RULES:
1. If ALL tests pass: Approve the fix (status: "SUCCESS")
2. If ANY test fails: Reject and provide a clear feedback (status: "NEEDS_REVISION")
3. Be specific about what went wrong
4. Suggest what the Fixer should focus on in the next iteration

You decide if the code is acceptable or not so be thorough but fair.
"""


def get_evaluation_prompt(file_path: str,
                          original_code: str,
                          fixed_code: str,
                          test_results: dict) -> str:
    """
    Generates prompt for the Judge to evaluate a fix attempt.
    
    Args:
        file_path: Path to the fixed file
        original_code: The original buggy code
        fixed_code: The Fixer's corrected code
        test_results: Results from pytest/unittest execution
        
    Returns:
        Formatted evaluation prompt
    """
    
    if test_results.get('passed'):
        tests_status = f"✓ APPROVED: {test_results['passed']} test(s)"
    else:
        tests_status = "✗ NO TESTS PASSED"
    
    if test_results.get('failed'):
        tests_status += f"\n✗ FAILED: {test_results['failed']} test(s)"
    
    prompt = f"""Evaluate this code fix and determine if it is acceptable.

FILE: {file_path}

ORIGINAL CODE:
```python
{original_code}
```

FIXED CODE:
```python
{fixed_code}
```

TEST RESULTS:
{tests_status}
"""
    
    
    if test_results.get('failures'):
        prompt += f"""

FAILURE DETAILS:
```
{test_results['failures']}
```
"""
    
    # Add error traces if available
    if test_results.get('errors'):
        prompt += f"""

ERROR TRACES:
```
{test_results['errors']}
```
"""
    
    prompt += """

YOUR TASK:
Analyze the test results and decide:

1. DECISION: Should this fix be accepted or rejected?
2. REASONING: Why did tests pass or fail?
3. FEEDBACK: What should the Fixer focus on next? (if rejected)

OUTPUT FORMAT (JSON):
{
  "decision": "SUCCESS" or "NEEDS_REVISION",
  "reasoning": "Clear explanation of your decision",
  "tests_passed": 5,
  "tests_failed": 0,
  "next_steps": "What to fix next (only if NEEDS_REVISION)",
  "estimated_iterations_remaining": 0
}

DECISION CRITERIA:
- SUCCESS: All tests pass, code runs without any errors
- NEEDS_REVISION: Any test fails OR code has runtime errors

Provide ONLY the JSON response, no additional text.
"""
    
    return prompt


# Feedback generation prompt
def get_feedback_prompt(failed_code: str, error_trace: str) -> str:
    """
    Generate clear and helpful feedback for the Fixer agent.
    """
    
    prompt = f"""The Fixer's code failed tests. Generate clear, actionable feedback.

FAILED CODE:
```python
{failed_code}
```

ERROR:
```
{error_trace}
```

Generate feedback that:
1. Identifies the problem clearly
2. Suggests a concrete fix approach
3. Explains why it failed

OUTPUT FORMAT:
{{
  "problem": "Describing te issue (one sentence or two maximum)",
  "explanation": "Why this causes the test to fail",
  "suggested_fix": "Specific action to take",
}}
"""
    
    return prompt


# Progress assessment prompt
def get_progress_assessment_prompt(iteration_history: list) -> str:
    """
    Assess the overall progress achieved after multiple iterations.
    
    Args:
        iteration_history: List of previous iteration results
    """
    
    history_text = "\n".join([
        f"Iteration {i+1}: {result['tests_passed']}/{result['tests_total']} tests passed"
        for i, result in enumerate(iteration_history)
    ])
    
    prompt = f"""Assess the refactoring progress over multiple iterations.

ITERATION HISTORY:
{history_text}

ANALYSIS QUESTIONS:
1. Is progress being made? (Are we getting closer to success?)
2. Are we stuck in a loop? (Same errors repeating?)
3. Should we continue or try a different approach? (Try a diffrent approach if the same errors are repeated for more than three times in a row)

OUTPUT (JSON):
{{
  "progress_trend": "improving" / "frozen" / "regressing",
  "stuck_in_loop": true/false,
  "recommendation": "CONTINUE" / "CHANGE_STRATEGY" / "CANCEL",
  "reasoning": "explanation",
  "max_iterations_suggested": int
}}
"""
    
    return prompt


# LOOP CONTROL
LOOP_CONTROL_PROMPT = """Based on test results, decide next action.

TEST RESULTS:
- Tests passed: {tests_passed}
- Tests failed: {tests_failed}
- Iteration count: {iteration}

DECISION RULES:
- If all tests pass: Return "COMPLETE"
- If tests fail and iteration < 12: Return "RETRY"
- If iteration >= 12: Return "MAX_ITERATIONS_REACHED"

Respond with ONLY one of these three words: COMPLETE, RETRY, or MAX_ITERATIONS_REACHED
"""


# Final validation prompt
FINAL_VALIDATION_PROMPT = """Perform final validation before marking code as complete.

CHECKLIST:
1. ✓ All unit tests pass
2. ✓ No syntax errors
3. ✓ Pylint score improved
4. ✓ Code follows PEP 8
5. ✓ All functions have docstrings
6. ✓ No obvious bugs remain

FIXED CODE:
{code}

Verify each item and respond:
{{
  "validation_passed": true/false,
  "checklist_results": {{
    "tests": "pass/fail",
    "syntax": "pass/fail",
    "quality": "pass/fail",
    "style": "pass/fail",
  }},
  "final_verdict": "APPROVED" or "NEEDS_MORE_WORK"
}}
"""