
#Agent Correcteur (The Fixer) - Corrige le code selon le plan de l'Auditeur.
import re
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompts import FIXER_SYSTEM_PROMPT
from src.tools.file_tools import read_file, write_file, check_syntax
from src.utils.logger import ActionType


class FixerAgent(BaseAgent):
  
    #agent responsable de la correction du code.
    
    #il lit le plan de l'Auditeur et applique les corrections.
 
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialise l'Agent Correcteur."""
        super().__init__(name="Fixer_Agent", model_name=model_name)
    
    def run(self, file_path: str, audit_report: Dict[str, Any], 
            sandbox_root: str, test_errors: Optional[str] = None) -> Dict[str, Any]:
        # Lire le contenu original
        try:
            original_code = read_file(file_path)
        except FileNotFoundError as e:
            return {"error": str(e), "success": False}
        
        # Construire le prompt
        input_prompt = self._build_prompt(file_path, original_code, audit_report, test_errors)
        
        # Appeler le LLM
        response = self.call_llm(input_prompt, FIXER_SYSTEM_PROMPT)
     
        fixed_code = self._extract_code(response)
        
        syntax_valid, syntax_error = check_syntax(fixed_code)
        
        if not syntax_valid:
            # Logger l'échec
            self.log_action(
                action=ActionType.FIX,
                details={
                    "file_fixed": file_path,
                    "input_prompt": input_prompt,
                    "output_response": response,
                    "syntax_error": syntax_error
                },
                status="FAILURE"
            )
            return {
                "success": False,
                "error": f"Le code corrigé contient des erreurs de syntaxe: {syntax_error}",
                "fixed_code": fixed_code
            }
        
        # Écrire le code corrigé
        try:
            write_file(file_path, fixed_code, sandbox_root)
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        
        # Logger le succès
        self.log_action(
            action=ActionType.FIX,
            details={
                "file_fixed": file_path,
                "input_prompt": input_prompt,
                "output_response": response,
                "original_lines": len(original_code.splitlines()),
                "fixed_lines": len(fixed_code.splitlines())
            },
            status="SUCCESS"
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "fixed_code": fixed_code,
            "original_code": original_code
        }
    
    def _build_prompt(self, file_path: str, original_code: str, 
                      audit_report: Dict[str, Any], test_errors: Optional[str]) -> str:
        #construit le prompt pour le LLM.
        prompt_parts = [
            f"fichier a corriger: {file_path}",
            "",
            "original code:",
            "```python",
            original_code,
            "```",
            "",
            "rapport daudit:"
        ]
        
        if audit_report.get("syntax_errors"):
            prompt_parts.append("\nsyntax errors:")
            for err in audit_report["syntax_errors"]:
                prompt_parts.append(f"  - Ligne {err.get('line', '?')}: {err.get('description', '')}")
                prompt_parts.append(f"    Suggestion: {err.get('fix_suggestion', '')}")
        
        if audit_report.get("logic_bugs"):
            prompt_parts.append("\nbugs logic:")
            for bug in audit_report["logic_bugs"]:
                prompt_parts.append(f"  - Ligne {bug.get('line', '?')} ({bug.get('function', '?')}): {bug.get('description', '')}")
                prompt_parts.append(f"    Comportement attendu: {bug.get('expected_behavior', '')}")
                prompt_parts.append(f"    Suggestion: {bug.get('fix_suggestion', '')}")
        
        if audit_report.get("code_smells"):
            prompt_parts.append("\ncode smel:")
            for smell in audit_report["code_smells"]:
                prompt_parts.append(f"  - Ligne {smell.get('line', '?')} ({smell.get('type', '?')}): {smell.get('description', '')}")
                prompt_parts.append(f"    Suggestion: {smell.get('fix_suggestion', '')}")
        
        if test_errors:
            prompt_parts.extend([
                "",
                "errors test (BOUCLE DE SELF-HEALING):",
                test_errors,
                "",
                "corrige le code pour succeder test."
            ])
        
        prompt_parts.extend([
            "",
            "produis le code corrige complet et fonctionnel."
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_code(self, response: str) -> str:
        """Extrait le code Python de la réponse du LLM."""
        
        response = response.strip()
        
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        pattern2 = r"```\s*(.*?)\s*```"
        matches2 = re.findall(pattern2, response, re.DOTALL)
        
        if matches2:
            code = max(matches2, key=len).strip()
            lines = code.split('\n')
            if lines and lines[0].lower() in ['python', 'py', 'python3']:
                code = '\n'.join(lines[1:])
            return code.strip()
        
        # si no markdown verifier code commence 
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ', 'def ', 'class ', '#', '"""', "'''")):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        return response.strip()
