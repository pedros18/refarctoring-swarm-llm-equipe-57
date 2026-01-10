#agent Auditeur (The auditor) - analyse le code et produit un plan de correction

import json
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompts import AUDITOR_SYSTEM_PROMPT
from src.tools.file_tools import read_file, check_syntax, run_pylint
from src.utils.logger import ActionType


class AuditorAgent(BaseAgent):
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
            super().__init__(name="Auditor_Agent", model_name=model_name)
    
    def run(self, file_path: str) -> Dict[str, Any]:
        try:
            code_content = read_file(file_path)
        except FileNotFoundError as e:
            return {"error": str(e), "success": False}
        
       
        syntax_valid, syntax_error = check_syntax(code_content)

        input_prompt = f"""Analyse ce fichier Python et produis un plan de refactoring:

FICHIER: {file_path}

SYNTAXE VALIDE: {syntax_valid}
{f"ERREUR DE SYNTAXE: {syntax_error}" if syntax_error else ""}

CODE:
```python
{code_content}
```

produi un rapport JSON avec les corrections suggested
"""
 
        response = self.call_llm(input_prompt, AUDITOR_SYSTEM_PROMPT)
        
        #json process
        analysis_result = self._parse_response(response, file_path)
        self.log_action(
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": file_path,
                "input_prompt": input_prompt,
                "output_response": response,
                "syntax_valid": syntax_valid,
                "issues_found": len(analysis_result.get("syntax_errors", [])) + 
                               len(analysis_result.get("logic_bugs", [])) + 
                               len(analysis_result.get("code_smells", []))
            },
            status="SUCCESS" if analysis_result.get("success", False) else "FAILURE"
        )
        
        return analysis_result
    
    def _parse_response(self, response: str, file_path: str) -> Dict[str, Any]:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            result["success"] = True
            result["raw_response"] = response
            return result
        except json.JSONDecodeError:
            return {
                "file_path": file_path,
                "syntax_errors": [],
                "logic_bugs": [],
                "code_smells": [],
                "overall_score": 0,
                "priority_fixes": [],
                "success": False,
                "raw_response": response,
                "parse_error": "Impossible de parser la réponse JSON du LLM"
            }
