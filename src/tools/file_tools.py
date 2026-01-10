
#module d'outils pour l'analyse et la manipulation de fichiers Python.
#utilise par les agents du refactoring swarm.

import os
import subprocess
import tempfile
import ast
from typing import Dict, List, Tuple, Optional


def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str, sandbox_root: str) -> bool:
    #only sandbox security
    abs_file = os.path.abspath(file_path)
    abs_sandbox = os.path.abspath(sandbox_root)
    
    if not abs_file.startswith(abs_sandbox):
        raise PermissionError(f"non hors du sandbox: {file_path}")
    
    os.makedirs(os.path.dirname(abs_file), exist_ok=True)
    
    with open(abs_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def list_python_files(directory: str) -> List[str]:
    python_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Erreur de syntaxe ligne {e.lineno}: {e.msg}"


def run_pylint(file_path: str) -> Dict:
    try:
        result = subprocess.run(
            ['pylint', file_path, '--output-format=json', '--disable=C0114,C0115,C0116'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        import json
        messages = []
        if result.stdout.strip():
            try:
                messages = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        score = 0.0
        for line in result.stderr.split('\n'):
            if 'rated at' in line:
                try:
                    score = float(line.split('rated at')[1].split('/')[0].strip())
                except (ValueError, IndexError):
                    pass
        
        return {
            "file": file_path,
            "score": score,
            "messages": messages,
            "issues_count": len(messages)
        }
    except subprocess.TimeoutExpired:
        return {"file": file_path, "error": "Timeout lors de l'analyse pylint"}
    except FileNotFoundError:
        return {"file": file_path, "error": "pylint non installé"}


def run_pytest(test_file: str, target_dir: str) -> Dict:
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = target_dir + ':' + env.get('PYTHONPATH', '')
        
        result = subprocess.run(
            ['pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=target_dir
        )
        
        passed = result.stdout.count(' PASSED')
        failed = result.stdout.count(' FAILED')
        errors = result.stdout.count(' ERROR')
        
        return {
            "test_file": test_file,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success": failed == 0 and errors == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"test_file": test_file, "error": "Timeout lors de l'exécution des tests", "success": False}
    except FileNotFoundError:
        return {"test_file": test_file, "error": "pytest non installé", "success": False}


def execute_code(code: str, timeout: int = 10) -> Dict:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout lors de l'exécution"}
    finally:
        os.unlink(temp_file)


def get_file_analysis(file_path: str) -> Dict:
    analysis = {
        "file_path": file_path,
        "exists": os.path.exists(file_path),
        "syntax_valid": False,
        "syntax_error": None,
        "pylint_report": None,
        "content": None
    }
    
    if not analysis["exists"]:
        return analysis
    
    #lecture continu
    analysis["content"] = read_file(file_path)

    is_valid, error = check_syntax(analysis["content"])
    analysis["syntax_valid"] = is_valid
    analysis["syntax_error"] = error
    
    #execute pylint
    if is_valid:
        analysis["pylint_report"] = run_pylint(file_path)
    
    return analysis
