"""
Prompts for the Fixer Agent
Role: Takes refactoring plan and fixes the actual code

"""

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

You are a expert code fixer - precise and minimal changes only.
"""
def get_fix_prompt(file_path: str, original_code: str, refactoring_plan: dict) -> str:
    """
    Generates the prompt to fix code based on auditor's refractoring plan.
    
    Args:
        file_path: Path to the file
        original_code: The buggy code
        refactoring_plan: JSON from the auditor with issues to fix
        
    Returns:
        Formatted prompt for the fixer agent
    """
    prompt = f"""Fix the following Python code according to the refactoring plan.

FILE: {file_path}

ORIGINAL CODE:
```python
{original_code}
```

REFACTORING PLAN:
{refactoring_plan}

INSTRUCTIONS:
1. Fix all CRITICAL issues first
2. Apply MAJOR improvements
3. Address MINOR issues if they don't require major restructuring
4. Add docstrings where missing
5. Ensure PEP 8 compliance
6. Fix the logical bugs
7. Preserve the original code when possible

OUTPUT:
Provide ONLY the corrected Python code, wrapped in ```python code blocks.
Do not include explanations, comments about changes, or anything else.
Just the clean, working Python code.

Example output format:
```python
def example_function(x, y):
    \"\"\"
    Calculate sum of two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
    \"\"\"
    return x + y
```
"""
    
    return prompt


def get_focused_fix_prompt(file_path: str, original_code: str, failed_attempt: str, error_message: str) -> str:
    """
    if the Judge report that the fix code is failed, this prompt helps the Fixer try again.
    
    Args:
        file_path: Path to file
        original_code: Original buggy code
        failed_attempt: The code that was just tried but failed
        error_message: Error from test execution
    """
    
    prompt = f"""Your previous fix attempt failed. Analyze and correct it.

FILE: {file_path}

ORIGINAL BUGGY CODE:
```python
{original_code}
```

YOUR FAILED FIX:
```python
{failed_attempt}
```

ERROR MESSAGE:
```
{error_message}
```

INSTRUCTIONS:
1. Identify what went wrong in your fix
2. The error message shows the specific problem
3. Provide a corrected version that addresses this error
4. Be more conservative - take small changes for safety

OUTPUT: Only the corrected Python code in ```python blocks.
"""
    
    return prompt


def get_incremental_fix_prompt(file_path: str,
                                original_code: str,
                                issues_subset: list) -> str:
    """
    Fix only specific issues (useful for large files with many problems).
    
    Args:
        file_path: Path to file
        original_code: The buggy code
        issues_subset: List of specific issues to address in this iteration
    """
    
    issues_text = "\n".join([f"- Line {issue['line']}: {issue['description']}" 
                              for issue in issues_subset])
    
    prompt = f"""Fix ONLY the following specific issues in this code.

FILE: {file_path}

CODE:
```python
{original_code}
```

ISSUES TO FIX (this iteration):
{issues_text}

IMPORTANT:
- Fix ONLY these specific issues
- Do not change anything else
- Maintain all other code exactly as is
- Merge the fixes with the rest of the code
- This is part of an incremental fixing process

OUTPUT: The code with only these specific fixes applied.
"""
    
    return prompt


def get_docstring_prompt(code: str) -> str:
    """
    Specialized prompt for adding documentation.
    """
    
    prompt = f"""Add proper docstrings to this Python code.

CODE:
```python
{code}
```

REQUIREMENTS:
1. Add module docstring at the top
2. Add docstrings to all functions and classes
3. Use Google-style or NumPy-style docstrings
4. Document parameters, return values, and exceptions
5. Keep docstrings concise but informative

Example format:
def function_name(param1, param2):
    \"\"\"
    Brief description of what the function does.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        type: Description of return value
        
    Raises:
        ValueError: When X happens
    \"\"\"

OUTPUT: The same code with docstrings added.
"""
    
    return prompt



SAFETY_CHECK_PROMPT = """Before applying your fix, perform a safety check:

ORIGINAL CODE:
{original_code}

YOUR PROPOSED FIX:
{fixed_code}

Answer these questions:
1. Does the fix preserve all original functionality?
2. Could the fix introduce new bugs?
3. Are all syntax rules followed?
4. Are the fixes followed the refractoring plan?

Respond with:
- "SAFE_TO_APPLY" if all checks pass
- "NEEDS_REVISION: [reason]" if there's a problem
"""


# Template for common fixes
COMMON_FIX_TEMPLATES = {
    "missing_colon": {
        "pattern": "def function_name(params)",
        "fix": "def function_name(params):"
    },
    
    "missing_import": {
        "pattern": "# Missing import for X",
        "fix": "import X  # Add at top of file"
    },
    
    "indentation_error": {
        "instruction": "Ensure consistent 4-space indentation throughout"
    },
    
    "undefined_variable": {
        "instruction": "Check variable names for typos and ensure all variables are defined before use"
    }
}
