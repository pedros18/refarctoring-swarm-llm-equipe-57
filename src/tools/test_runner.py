"""
Test Runner Tool - Interface avec Pytest
Author: Toolsmith
Description: Exécution et analyse des tests unitaires
"""
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET


class TestRunner:
    """Gestionnaire d'exécution de tests avec Pytest"""
    
    def __init__(self, timeout: int = 60):
        """
        Initialise le runner de tests
        
        Args:
            timeout: Timeout en secondes pour l'exécution des tests
        """
        self.timeout = timeout
        self.last_results = None
    
    def run_pytest(self, target_path: str, verbose: bool = True) -> Dict:
        """
        Lance Pytest sur un fichier ou dossier
        
        Args:
            target_path: Chemin du fichier/dossier de test
            verbose: Mode verbeux
            
        Returns:
            Dict: Résultats des tests
        """
        try:
            # Préparer la commande pytest
            cmd = [
                'pytest',
                target_path,
                '--tb=short',  # Traceback court
                '--json-report',  # Rapport JSON
                '--json-report-file=pytest_report.json',
                '-v' if verbose else '-q'
            ]
            
            # Exécuter pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Parser les résultats
            test_results = self._parse_pytest_output(result.stdout, result.stderr)
            test_results['exit_code'] = result.returncode
            test_results['success'] = result.returncode == 0
            
            self.last_results = test_results
            return test_results
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': f'Tests timeout après {self.timeout}s',
                'success': False
            }
        except FileNotFoundError:
            return {
                'status': 'error',
                'error': 'Pytest non installé ou introuvable',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'success': False
            }
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict:
        """
        Parse la sortie de pytest
        
        Args:
            stdout: Sortie standard
            stderr: Sortie erreur
            
        Returns:
            Dict: Résultats parsés
        """
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'duration': 0.0,
            'failures': [],
            'status': 'completed'
        }
        
        # Chercher le résumé (ex: "5 passed, 2 failed in 1.23s")
        summary_pattern = r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error'
        for match in re.finditer(summary_pattern, stdout):
            if match.group(1):
                results['passed'] = int(match.group(1))
            elif match.group(2):
                results['failed'] = int(match.group(2))
            elif match.group(3):
                results['skipped'] = int(match.group(3))
            elif match.group(4):
                results['errors'] = int(match.group(4))
        
        results['total'] = results['passed'] + results['failed'] + results['skipped'] + results['errors']
        
        # Extraire la durée
        duration_match = re.search(r'in ([\d.]+)s', stdout)
        if duration_match:
            results['duration'] = float(duration_match.group(1))
        
        # Extraire les échecs
        results['failures'] = self._extract_failures(stdout)
        
        return results
    
    def _extract_failures(self, output: str) -> List[Dict]:
        """
        Extrait les détails des tests échoués
        
        Args:
            output: Sortie de pytest
            
        Returns:
            List[Dict]: Liste des échecs avec détails
        """
        failures = []
        
        # Pattern pour identifier les échecs
        # Exemple: "test_file.py::test_function FAILED"
        fail_pattern = r'([\w/]+\.py)::([\w_]+)\s+FAILED'
        
        for match in re.finditer(fail_pattern, output):
            file_path = match.group(1)
            test_name = match.group(2)
            
            failures.append({
                'file': file_path,
                'test': test_name,
                'full_name': f"{file_path}::{test_name}"
            })
        
        return failures
    
    def run_single_test(self, test_path: str) -> Dict:
        """
        Lance un seul test spécifique
        
        Args:
            test_path: Chemin du test (format: file.py::test_name)
            
        Returns:
            Dict: Résultat du test
        """
        return self.run_pytest(test_path, verbose=True)
    
    def check_test_file_exists(self, file_path: str) -> bool:
        """
        Vérifie si un fichier de test existe
        
        Args:
            file_path: Chemin du fichier de test
            
        Returns:
            bool: True si existe
        """
        return Path(file_path).exists()
    
    def discover_tests(self, directory: str) -> List[str]:
        """
        Découvre tous les fichiers de test dans un répertoire
        
        Args:
            directory: Répertoire à scanner
            
        Returns:
            List[str]: Liste des fichiers de test trouvés
        """
        try:
            test_dir = Path(directory)
            
            # Chercher les fichiers test_*.py et *_test.py
            test_files = []
            test_files.extend(test_dir.glob('**/test_*.py'))
            test_files.extend(test_dir.glob('**/*_test.py'))
            
            return sorted([str(f) for f in test_files])
            
        except Exception as e:
            print(f"❌ Erreur découverte tests: {e}")
            return []
    
    def generate_test_report(self, results: Dict = None) -> str:
        """
        Génère un rapport textuel des résultats
        
        Args:
            results: Résultats des tests (utilise last_results si None)
            
        Returns:
            str: Rapport formaté
        """
        if results is None:
            results = self.last_results
        
        if results is None:
            return "Aucun test exécuté"
        
        report = []
        report.append("🧪 RAPPORT DE TESTS")
        report.append("=" * 60)
        
        # Statut global
        status_emoji = "✅" if results.get('success') else "❌"
        report.append(f"\n{status_emoji} Statut: {'SUCCÈS' if results.get('success') else 'ÉCHEC'}")
        
        # Statistiques
        report.append(f"\n📊 Statistiques:")
        report.append(f"   - Total: {results.get('total', 0)}")
        report.append(f"   - Réussis: {results.get('passed', 0)} ✅")
        report.append(f"   - Échoués: {results.get('failed', 0)} ❌")
        report.append(f"   - Ignorés: {results.get('skipped', 0)} ⏭️")
        report.append(f"   - Erreurs: {results.get('errors', 0)} 💥")
        report.append(f"   - Durée: {results.get('duration', 0):.2f}s ⏱️")
        
        # Taux de réussite
        if results.get('total', 0) > 0:
            success_rate = (results.get('passed', 0) / results['total']) * 100
            report.append(f"\n🎯 Taux de réussite: {success_rate:.1f}%")
        
        # Détails des échecs
        failures = results.get('failures', [])
        if failures:
            report.append(f"\n❌ Tests échoués ({len(failures)}):")
            for fail in failures:
                report.append(f"   - {fail['full_name']}")
        
        return "\n".join(report)
    
    def run_with_coverage(self, target_path: str) -> Dict:
        """
        Lance les tests avec couverture de code
        
        Args:
            target_path: Chemin cible
            
        Returns:
            Dict: Résultats avec couverture
        """
        try:
            cmd = [
                'pytest',
                target_path,
                '--cov',
                '--cov-report=term',
                '--cov-report=json:coverage.json',
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Parser résultats
            test_results = self._parse_pytest_output(result.stdout, result.stderr)
            
            # Lire le rapport de couverture
            coverage_data = self._read_coverage_report()
            test_results['coverage'] = coverage_data
            
            return test_results
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'success': False
            }
    
    def _read_coverage_report(self) -> Optional[Dict]:
        """
        Lit le rapport de couverture JSON
        
        Returns:
            Dict: Données de couverture ou None
        """
        try:
            coverage_file = Path('coverage.json')
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    data = json.load(f)
                    return {
                        'percent_covered': data.get('totals', {}).get('percent_covered', 0),
                        'lines_covered': data.get('totals', {}).get('covered_lines', 0),
                        'lines_total': data.get('totals', {}).get('num_statements', 0)
                    }
        except Exception as e:
            print(f"⚠️ Impossible de lire coverage.json: {e}")
        
        return None
    
    def validate_test_structure(self, test_code: str) -> Dict:
        """
        Valide la structure d'un fichier de test
        
        Args:
            test_code: Code source du test
            
        Returns:
            Dict: Validation (nombre de tests, fixtures, etc.)
        """
        import ast
        
        try:
            tree = ast.parse(test_code)
            
            # Compter les fonctions de test
            test_functions = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
            ]
            
            # Compter les fixtures
            fixtures = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and 
                any(d.id == 'fixture' for d in node.decorator_list if isinstance(d, ast.Name))
            ]
            
            return {
                'valid': True,
                'test_count': len(test_functions),
                'fixture_count': len(fixtures),
                'test_names': test_functions,
                'has_imports': any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
            }
            
        except SyntaxError as e:
            return {
                'valid': False,
                'error': str(e),
                'line': e.lineno
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


# Test unitaire
if __name__ == "__main__":
    runner = TestRunner()
    
    # Test avec un exemple simple
    print("🧪 Test du TestRunner")
    
    # Créer un fichier de test temporaire
    test_code = '''
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

def test_failure():
    assert 1 == 2  # Ceci va échouer
'''
    
    # Valider la structure
    validation = runner.validate_test_structure(test_code)
    print("\nValidation structure:", validation)
    
    # Découvrir les tests
    tests = runner.discover_tests('.')
    print(f"\nTests découverts: {len(tests)}")