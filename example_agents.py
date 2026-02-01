"""
Example Agents with OpenRouter Integration
Production-ready examples showing how to build agents that:
1. Call OpenRouter API
2. Log properly with the logging system
3. Handle errors

Copy these patterns when building your own agents!
"""

import os
import sys

# Add src to path so we can import logger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from openrouter_client import OpenRouterClient
from utils.logger import log_experiment, ActionType


class AuditorAgent:
    """
    Auditor Agent - Analyzes code for issues
    
    Usage:
        auditor = AuditorAgent()
        result = auditor.analyze_file("path/to/file.py")
    """
    
    def __init__(self, model="anthropic/claude-3.5-sonnet"):
        """Initialize the Auditor Agent"""
        self.client = OpenRouterClient(model=model)
        self.agent_name = "Auditor_Agent"
        self.model = model
    
    def analyze_file(self, filepath):
        """
        Analyze a Python file for issues
        
        Args:
            filepath: Path to Python file to analyze
            
        Returns:
            dict with success status and analysis
        """
        print(f"\n🔍 [{self.agent_name}] Analyzing: {filepath}")
        
        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        
        # Prepare prompts
        system_prompt = """You are an expert Python code auditor. Analyze code and identify:
1. Syntax errors
2. Logic bugs
3. Missing docstrings
4. PEP 8 violations
5. Code smells and anti-patterns

Return a structured analysis with:
- Issue type
- Severity (HIGH/MEDIUM/LOW)
- Line number (if applicable)
- Description
- Suggested fix"""
        
        prompt = f"""Analyze this Python file: {os.path.basename(filepath)}

Code:
```python
{code}
```

Provide a detailed analysis of all issues found."""
        
        # Call OpenRouter API
        try:
            response = self.client.generate(prompt, system_prompt, max_tokens=2000)
            
            # ✅ CRITICAL: Log the interaction
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": filepath,
                    "input_prompt": prompt,           # MANDATORY
                    "output_response": response,      # MANDATORY
                    "system_prompt": system_prompt,
                    "code_length": len(code),
                },
                status="SUCCESS"
            )
            
            print(f"✅ Analysis complete!")
            return {
                'success': True,
                'filepath': filepath,
                'analysis': response,
                'code_length': len(code)
            }
            
        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # ✅ Log failures too!
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": filepath,
                    "input_prompt": prompt,
                    "output_response": f"ERROR: {str(e)}",
                    "error": str(e),
                },
                status="ERROR"
            )
            
            return {'success': False, 'error': error_msg}


class FixerAgent:
    """
    Fixer Agent - Fixes code based on issues found
    
    Usage:
        fixer = FixerAgent()
        result = fixer.fix_file("path/to/file.py", issues_description)
    """
    
    def __init__(self, model="anthropic/claude-3.5-sonnet"):
        """Initialize the Fixer Agent"""
        self.client = OpenRouterClient(model=model)
        self.agent_name = "Fixer_Agent"
        self.model = model
    
    def fix_file(self, filepath, issues):
        """
        Fix a Python file based on identified issues
        
        Args:
            filepath: Path to Python file to fix
            issues: Description of issues to fix
            
        Returns:
            dict with success status and fixed code
        """
        print(f"\n🔧 [{self.agent_name}] Fixing: {filepath}")
        
        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        
        # Prepare prompts
        system_prompt = """You are an expert Python code fixer. Given code and issues:
1. Fix all identified problems
2. Maintain original functionality
3. Add proper docstrings (Google style)
4. Follow PEP 8 standards
5. Improve code quality

IMPORTANT: Return ONLY the complete fixed Python code.
Do not include markdown formatting, explanations, or any text before/after the code."""
        
        prompt = f"""Fix this Python file: {os.path.basename(filepath)}

Original Code:
```python
{original_code}
```

Issues to fix:
{issues}

Return ONLY the complete fixed Python code, nothing else."""
        
        # Call OpenRouter API
        try:
            response = self.client.generate(prompt, system_prompt, max_tokens=3000)
            
            # Clean response (remove markdown if present)
            fixed_code = response.strip()
            if fixed_code.startswith('```python'):
                fixed_code = fixed_code.split('```python')[1].split('```')[0].strip()
            elif fixed_code.startswith('```'):
                fixed_code = fixed_code.split('```')[1].split('```')[0].strip()
            
            # ✅ CRITICAL: Log the interaction
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.FIX,
                details={
                    "file_fixed": filepath,
                    "input_prompt": prompt,              # MANDATORY
                    "output_response": response,         # MANDATORY
                    "system_prompt": system_prompt,
                    "original_length": len(original_code),
                    "fixed_length": len(fixed_code),
                    "issues_count": len(issues.split('\n')),
                },
                status="SUCCESS"
            )
            
            print(f"✅ Code fixed! ({len(original_code)} → {len(fixed_code)} chars)")
            return {
                'success': True,
                'filepath': filepath,
                'original_code': original_code,
                'fixed_code': fixed_code,
            }
            
        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.FIX,
                details={
                    "file_fixed": filepath,
                    "input_prompt": prompt,
                    "output_response": f"ERROR: {str(e)}",
                    "error": str(e),
                },
                status="ERROR"
            )
            
            return {'success': False, 'error': error_msg}


class TestGeneratorAgent:
    """
    Test Generator Agent - Generates unit tests for code
    
    Usage:
        generator = TestGeneratorAgent()
        result = generator.generate_tests("path/to/file.py")
    """
    
    def __init__(self, model="anthropic/claude-3.5-sonnet"):
        """Initialize the Test Generator Agent"""
        self.client = OpenRouterClient(model=model)
        self.agent_name = "TestGenerator_Agent"
        self.model = model
    
    def generate_tests(self, filepath):
        """
        Generate unit tests for a Python file
        
        Args:
            filepath: Path to Python file to test
            
        Returns:
            dict with success status and test code
        """
        print(f"\n🧪 [{self.agent_name}] Generating tests for: {filepath}")
        
        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        
        # Prepare prompts
        system_prompt = """You are an expert Python test generator. Given code:
1. Generate comprehensive pytest unit tests
2. Cover normal cases, edge cases, and error conditions
3. Use descriptive test names (test_<function>_<scenario>)
4. Include docstrings in test functions
5. Use proper assertions

IMPORTANT: Return ONLY valid Python pytest code.
Do not include explanations or markdown formatting."""
        
        prompt = f"""Generate pytest unit tests for: {os.path.basename(filepath)}

Code to test:
```python
{code}
```

Generate complete pytest test code with:
- Test class(es) with proper naming
- Multiple test methods covering different scenarios
- Edge case and error handling tests
- Clear, descriptive test names"""
        
        # Call OpenRouter API
        try:
            response = self.client.generate(prompt, system_prompt, max_tokens=2500)
            
            # Clean response
            test_code = response.strip()
            if test_code.startswith('```python'):
                test_code = test_code.split('```python')[1].split('```')[0].strip()
            elif test_code.startswith('```'):
                test_code = test_code.split('```')[1].split('```')[0].strip()
            
            # ✅ CRITICAL: Log the interaction
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.GENERATION,
                details={
                    "file_tested": filepath,
                    "input_prompt": prompt,              # MANDATORY
                    "output_response": response,         # MANDATORY
                    "system_prompt": system_prompt,
                    "test_code_length": len(test_code),
                },
                status="SUCCESS"
            )
            
            print(f"✅ Tests generated! ({len(test_code)} chars)")
            return {
                'success': True,
                'filepath': filepath,
                'test_code': test_code,
            }
            
        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model,
                action=ActionType.GENERATION,
                details={
                    "file_tested": filepath,
                    "input_prompt": prompt,
                    "output_response": f"ERROR: {str(e)}",
                    "error": str(e),
                },
                status="ERROR"
            )
            
            return {'success': False, 'error': error_msg}


def demo_workflow():
    """
    Demonstration workflow showing all agents working together
    This is an example of how your main.py might orchestrate agents
    """
    print("="*70)
    print("🤖 REFACTORING SWARM - DEMO WORKFLOW")
    print("="*70)
    print("\nThis demonstrates:")
    print("1. Auditor analyzes code")
    print("2. Fixer fixes issues")
    print("3. TestGenerator creates tests")
    print("4. All actions are logged properly")
    
    # Check if test dataset exists
    test_file = "sandbox/test_dataset/test_logic_bugs.py"
    
    if not os.path.exists(test_file):
        print(f"\n⚠️  Test file not found: {test_file}")
        print("\n💡 Run this first: python generate_test_dataset.py")
        return False
    
    # Step 1: Auditor analyzes
    print("\n" + "-"*70)
    print("STEP 1: AUDITOR ANALYSIS")
    print("-"*70)
    auditor = AuditorAgent()
    analysis_result = auditor.analyze_file(test_file)
    
    if not analysis_result['success']:
        print(f"\n❌ Workflow stopped: Auditor failed")
        return False
    
    # Step 2: Fixer fixes the code
    print("\n" + "-"*70)
    print("STEP 2: FIXER FIXING CODE")
    print("-"*70)
    fixer = FixerAgent()
    fix_result = fixer.fix_file(test_file, analysis_result['analysis'])
    
    if not fix_result['success']:
        print(f"\n❌ Workflow stopped: Fixer failed")
        return False
    
    # Optional: Save fixed code
    output_file = test_file.replace('.py', '_fixed.py')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fix_result['fixed_code'])
        print(f"💾 Fixed code saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save fixed code: {e}")
    
    # Step 3: Generate tests
    print("\n" + "-"*70)
    print("STEP 3: TEST GENERATOR")
    print("-"*70)
    test_gen = TestGeneratorAgent()
    test_result = test_gen.generate_tests(test_file)
    
    if not test_result['success']:
        print(f"\n❌ Workflow stopped: Test generator failed")
        return False
    
    # Optional: Save test code
    test_output_file = test_file.replace('.py', '_test.py')
    try:
        with open(test_output_file, 'w', encoding='utf-8') as f:
            f.write(test_result['test_code'])
        print(f"💾 Test code saved to: {test_output_file}")
    except Exception as e:
        print(f"⚠️  Could not save test code: {e}")
    
    # Verify logging
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70)
    print(f"\n📊 Results:")
    print(f"   • Analyzed: {test_file}")
    print(f"   • Fixed code: {len(fix_result['fixed_code'])} chars")
    print(f"   • Test code: {len(test_result['test_code'])} chars")
    print(f"   • Logs: logs/experiment_data.json")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Run: python validate_logs.py")
    print(f"   2. Run: python generate_quality_report.py")
    print(f"   3. Review fixed code: {output_file}")
    print(f"   4. Review test code: {test_output_file}")
    
    return True


if __name__ == "__main__":
    """Run the demo workflow"""
    success = demo_workflow()
    
    if success:
        print("\n" + "="*70)
        print("🎉 Demo successful! All agents working correctly!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠️  Demo incomplete. Check errors above.")
        print("="*70)
    
    exit(0 if success else 1)