"""
File Tools - Utility functions for file operations, syntax checking, and linting
"""
import os
import ast
import subprocess
import json
from typing import Tuple, List, Dict, Any, Optional


def read_file(file_path: str) -> str:
    """Read and return file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str, sandbox_root: str = None) -> bool:
    """Write content to file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """Check if Python code has valid syntax."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def run_pylint(file_path: str) -> Dict[str, Any]:
    """Run pylint on a file and return results."""
    try:
        result = subprocess.run(
            ['pylint', file_path, '--output-format=json', '--score=yes'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        issues = []
        if result.stdout.strip():
            try:
                issues = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        score = 0.0
        for line in result.stderr.split('\n'):
            if 'rated at' in line:
                try:
                    score = float(line.split('rated at')[1].split('/')[0].strip())
                except:
                    pass
        
        return {
            'score': score,
            'issues': issues,
            'total_issues': len(issues)
        }
    except Exception as e:
        return {'score': 0.0, 'issues': [], 'error': str(e)}


def run_pytest(test_file: str, sandbox_root: str = None, timeout: int = 60) -> Dict[str, Any]:
    """Run pytest on a test file."""
    try:
        # If sandbox_root is provided and test_file is inside it, use just the filename
        if sandbox_root and os.path.isdir(sandbox_root):
            cwd = sandbox_root
            # Use just the filename if the full path starts with sandbox_root
            if test_file.startswith(sandbox_root):
                test_file = os.path.basename(test_file)
            elif os.path.isabs(test_file):
                test_file = os.path.basename(test_file)
        else:
            cwd = None
        
        result = subprocess.run(
            ['pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        stdout = result.stdout
        stderr = result.stderr
        output = stdout + stderr
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        errors = output.count(' ERROR')
        
        return {
            'success': result.returncode == 0,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'output': output,
            'stdout': stdout,
            'stderr': stderr,
            'return_code': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout', 'output': '', 'stdout': '', 'stderr': '', 'passed': 0, 'failed': 0}
    except Exception as e:
        return {'success': False, 'error': str(e), 'output': '', 'stdout': '', 'stderr': '', 'passed': 0, 'failed': 0}


def list_python_files(directory: str) -> List[str]:
    """List all Python files in a directory (excluding test files)."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))
    
    return sorted(python_files)


def get_file_analysis(file_path: str) -> Dict[str, Any]:
    """Get comprehensive analysis of a Python file."""
    try:
        content = read_file(file_path)
        syntax_valid, syntax_error = check_syntax(content)
        pylint_result = run_pylint(file_path)
        
        return {
            'file_path': file_path,
            'content': content,
            'syntax_valid': syntax_valid,
            'syntax_error': syntax_error,
            'pylint_score': pylint_result.get('score', 0),
            'pylint_issues': pylint_result.get('issues', [])
        }
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'syntax_valid': False
        }
