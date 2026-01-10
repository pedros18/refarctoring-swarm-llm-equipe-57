#agent testeur (The judge) - Genere et execute les tests unitaires...

import os
import re
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompts import TESTER_SYSTEM_PROMPT
from src.tools.file_tools import read_file, write_file, run_pytest
from src.utils.logger import ActionType


class TesterAgent(BaseAgent):
   #agent responsable de la generation et execution des tests
    
    #genere des tests unitaires qui valident la correction fonctionnelle

    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        #init d'agent testeur
        super().__init__(name="Tester_Agent", model_name=model_name)
    
    def run(self, file_path: str, sandbox_root: str) -> Dict[str, Any]:
        #lire le code corrig
        try:
            code_content = read_file(file_path)
        except FileNotFoundError as e:
            return {"error": str(e), "success": False}
        
        #generer les tests
        test_result = self._generate_tests(file_path, code_content, sandbox_root)
        
        if not test_result["success"]:
            return test_result
        
        #execut les tests
        test_file_path = test_result["test_file_path"]
        execution_result = run_pytest(test_file_path, sandbox_root)
        
        #logger l'action
        self.log_action(
            action=ActionType.GENERATION,
            details={
                "file_tested": file_path,
                "input_prompt": test_result["input_prompt"],
                "output_response": test_result["output_response"],
                "test_file": test_file_path,
                "tests_passed": execution_result.get("passed", 0),
                "tests_failed": execution_result.get("failed", 0)
            },
            status="SUCCESS" if execution_result.get("success", False) else "FAILURE"
        )
        
        return {
            "success": execution_result.get("success", False),
            "test_file_path": test_file_path,
            "test_code": test_result["test_code"],
            "execution_result": execution_result,
            "passed": execution_result.get("passed", 0),
            "failed": execution_result.get("failed", 0),
            "stdout": execution_result.get("stdout", ""),
            "stderr": execution_result.get("stderr", "")
        }
    
    def _generate_tests(self, file_path: str, code_content: str, 
                        sandbox_root: str) -> Dict[str, Any]:
        file_name = os.path.basename(file_path)
        module_name = os.path.splitext(file_name)[0]
        
        #prompt build
        input_prompt = f"""Génère des tests unitaires pytest pour ce fichier Python:

FICHIER: {file_path}
MODULE: {module_name}

CODE À TESTER:
```python
{code_content}
```

INSTRUCTIONS:
1. Importe le module avec: from {module_name} import *
2. Teste chaque fonction avec des assertions précises
3. Inclus des tests pour les edge cases
4. Les tests doivent vérifier le comportement ATTENDU (pas le comportement bugué)

Génère le fichier de test complet.
"""
        
        response = self.call_llm(input_prompt, TESTER_SYSTEM_PROMPT)
        test_code = self._extract_test_code(response)
        test_file_name = f"test_{module_name}.py"
        test_file_path = os.path.join(sandbox_root, test_file_name)
        
        try:
            write_file(test_file_path, test_code, sandbox_root)
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'écriture du fichier de test: {e}"
            }
        
        return {
            "success": True,
            "test_file_path": test_file_path,
            "test_code": test_code,
            "input_prompt": input_prompt,
            "output_response": response
        }
    
    def _extract_test_code(self, response: str) -> str:

        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def validate_fix(self, file_path: str, sandbox_root: str) -> Dict[str, Any]:
        """
        Valide qu'un fichier corrigé passe tous les tests.
        
        Args:
            file_path: Chemin vers le fichier corrigé.
            sandbox_root: Racine du sandbox.
            
        Returns:
            Résultat de la validation.
        """
        return self.run(file_path, sandbox_root)
