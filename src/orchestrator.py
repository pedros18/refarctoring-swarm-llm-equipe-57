#orchestrateur du Refactoring Swarm.
#gerant de workflow entre les agents Auditor, Fixer et Tester.

import os
import time
from typing import Dict, Any, List
from colorama import Fore, Style, init
from src.agents.auditor_agent import AuditorAgent
from src.agents.fixer_agent import FixerAgent
from src.agents.tester_agent import TesterAgent
from src.tools.file_tools import list_python_files, get_file_analysis
from src.utils.logger import log_experiment, ActionType

#init colorama
init(autoreset=True)


class RefactoringOrchestrator:
    
    MAX_ITERATIONS = 5  #nb max itiration slfhealing (increased for complex cases)
    
    def __init__(self, target_dir: str, model_name: str = "gemini-2.0-flash"):
        self.target_dir = os.path.abspath(target_dir)
        self.model_name = model_name
        
        #init agents
        self.auditor = AuditorAgent(model_name=model_name)
        self.fixer = FixerAgent(model_name=model_name)
        self.tester = TesterAgent(model_name=model_name)
        
        #stats brk
        self.stats = {
            "files_processed": 0,
            "files_fixed": 0,
            "files_failed": 0,
            "total_iterations": 0
        }
    
    def run(self) -> Dict[str, Any]:

        python_files = list_python_files(self.target_dir)
        
        if not python_files:
            print(f"{Fore.RED}no fichier Python trouv dans {self.target_dir}")
            return {"success": False, "error": "no fichier python trouv"}
        
        print(f"{Fore.GREEN}{len(python_files)} fichiers python trouv:\n")
        for f in python_files:
            print(f"- {os.path.basename(f)}")
        print()
        
        results = []
        
        # chaque fichier wahdo
        for file_path in python_files:
            result = self._process_file(file_path)
            results.append(result)
            self.stats["files_processed"] += 1
            
            if result.get("success"):
                self.stats["files_fixed"] += 1
            else:
                self.stats["files_failed"] += 1
        
        self._print_summary()
        
        return {
            "success": self.stats["files_failed"] == 0,
            "stats": self.stats,
            "results": results
        }
    
    def _process_file(self, file_path: str) -> Dict[str, Any]:
        file_name = os.path.basename(file_path)
        print(f"{Fore.CYAN}traitement de: {file_name}")
        
        # Étape 1: Analyse initiale
        print(f"\n{Fore.YELLOW}etap 1 analyse")
        initial_analysis = get_file_analysis(file_path)
        
        if not initial_analysis["syntax_valid"]:
            print(f"{Fore.RED}erreur de syntaxe detect: {initial_analysis['syntax_error']}")
        
        # Étape 2: Audit par l'Auditeur
        print(f"\n{Fore.YELLOW}etap 2 audit par l'agent auditeur")
        audit_report = self.auditor.run(file_path)
        
        if not audit_report.get("success"):
            print(f"{Fore.RED}echec de l'audit")
        else:
            issues = (len(audit_report.get("syntax_errors", [])) + 
                     len(audit_report.get("logic_bugs", [])) + 
                     len(audit_report.get("code_smells", [])))
            print(f"{Fore.GREEN}audit finish - {issues} problem identifier")
        
        #slf healin loop
        iteration = 0
        test_errors = None
        fix_success = False
        
        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            self.stats["total_iterations"] += 1
            print(f"\n{Fore.YELLOW}etap 3.{iteration}] corriger par l'agent Fixer (iteration {iteration}/{self.MAX_ITERATIONS})")
            fix_result = self.fixer.run(
                file_path=file_path,
                audit_report=audit_report,
                sandbox_root=self.target_dir,
                test_errors=test_errors
            )
            
            if not fix_result.get("success"):
                print(f"{Fore.RED}echec de la correction: {fix_result.get('error', 'Erreur inconnue')}")
                continue
            
            print(f"{Fore.GREEN}Code corrige avec succes")
            
            print(f"\n{Fore.YELLOW}etape 4.{iteration}] validation par l'agent tester")
            
            time.sleep(2)
            
            test_result = self.tester.run(file_path, self.target_dir)
            
            if test_result.get("success"):
                print(f"{Fore.GREEN}tous les tests c bon! ({test_result.get('passed', 0)} tests)")
                fix_success = True
                break
            else:
                failed = test_result.get("failed", 0)
                print(f"{Fore.RED}{failed} test echec")
                
                test_errors = self._format_test_errors(test_result)
                
                if iteration < self.MAX_ITERATIONS:
                    print(f"{Fore.YELLOW}looper au fixer avec les erreurs")
        
        if fix_success:
            print(f"\n{Fore.GREEN} {file_name} traiter avec succcs en {iteration} etapes")
        else:
            print(f"\n{Fore.RED} {file_name} non corriger apres {self.MAX_ITERATIONS} etapes")
        
        return {
            "file": file_path,
            "success": fix_success,
            "iterations": iteration,
            "audit_report": audit_report,
            "final_test_result": test_result if 'test_result' in dir() else None
        }
    
    def _format_test_errors(self, test_result: Dict[str, Any]) -> str:
        errors = []
        
        stdout = test_result.get("stdout", "")
        stderr = test_result.get("stderr", "")
        
        if stdout:
            errors.append("STDOUT des tests:")
            errors.append(stdout[:2000])
        
        if stderr:
            errors.append("\nSTDERR des tests:")
            errors.append(stderr[:1000])
        
        return "\n".join(errors)
    
    def _print_summary(self) -> None:
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN} resume du refactoring")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}   Fichiers traites:  {self.stats['files_processed']}")
        print(f"{Fore.GREEN}   Fichiers corriges: {self.stats['files_fixed']}")
        print(f"{Fore.RED}   Fichiers echoues:  {self.stats['files_failed']}")
        print(f"{Fore.YELLOW}   Total itérations:  {self.stats['total_iterations']}")
        
        if self.stats['files_failed'] == 0:
            print(f"\n{Fore.GREEN}tous les fichiers corriger")
        else:
            print(f"\n{Fore.YELLOW}il ya des fichiers necessitent corriger manuelement")
        
        print(f"{Fore.CYAN}{'='*60}\n")
