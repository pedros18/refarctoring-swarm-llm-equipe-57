"""
Code Analyzer Tool - Interface avec Pylint et analyses statiques
Author: Toolsmith
Description: Analyse de code Python (qualité, bugs, complexité)
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import ast
import re


class CodeAnalyzer:
    """Analyseur de code Python avec Pylint et métriques"""
    
    def __init__(self):
        """Initialise l'analyseur"""
        self.pylint_config = {
            'disable': [],  # Désactiver certains warnings si besoin
            'max-line-length': 100
        }
    
    def run_pylint(self, file_path: str) -> Dict:
        """
        Lance Pylint sur un fichier Python
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Dict: Résultats d'analyse (score, issues, etc.)
        """
        try:
            # Commande Pylint avec output JSON
            cmd = [
                'pylint',
                file_path,
                '--output-format=json',
                '--score=yes'
            ]
            
            # Exécuter Pylint
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parser le JSON
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            # Extraire le score de stderr (Pylint met le score là)
            score = self._extract_score(result.stderr)
            
            return {
                'file': file_path,
                'score': score,
                'issues': issues,
                'total_issues': len(issues),
                'error_count': sum(1 for i in issues if i['type'] == 'error'),
                'warning_count': sum(1 for i in issues if i['type'] == 'warning'),
                'status': 'success'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'file': file_path,
                'status': 'timeout',
                'error': 'Pylint timeout après 30s'
            }
        except Exception as e:
            return {
                'file': file_path,
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_score(self, stderr_text: str) -> Optional[float]:
        """
        Extrait le score Pylint du stderr
        
        Args:
            stderr_text: Sortie stderr de Pylint
            
        Returns:
            float: Score ou None
        """
        # Regex pour trouver "Your code has been rated at X.XX/10"
        match = re.search(r'rated at ([\d.]+)/10', stderr_text)
        if match:
            return float(match.group(1))
        return None
    
    def analyze_syntax(self, code: str, file_path: str = "<string>") -> Dict:
        """
        Analyse syntaxique avec AST Python
        
        Args:
            code: Code source Python
            file_path: Nom du fichier (pour messages d'erreur)
            
        Returns:
            Dict: Résultats d'analyse syntaxique
        """
        try:
            tree = ast.parse(code, filename=file_path)
            
            # Compter les éléments
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
            
            return {
                'valid_syntax': True,
                'functions_count': len(functions),
                'classes_count': len(classes),
                'imports_count': len(imports),
                'total_nodes': sum(1 for _ in ast.walk(tree)),
                'status': 'success'
            }
            
        except SyntaxError as e:
            return {
                'valid_syntax': False,
                'error': str(e),
                'line': e.lineno,
                'offset': e.offset,
                'status': 'syntax_error'
            }
        except Exception as e:
            return {
                'valid_syntax': False,
                'error': str(e),
                'status': 'error'
            }
    
    def check_docstrings(self, code: str) -> Dict:
        """
        Vérifie la présence de docstrings
        
        Args:
            code: Code source Python
            
        Returns:
            Dict: Statistiques sur les docstrings
        """
        try:
            tree = ast.parse(code)
            
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            
            # Vérifier docstrings
            funcs_with_docs = sum(1 for f in functions if ast.get_docstring(f))
            classes_with_docs = sum(1 for c in classes if ast.get_docstring(c))
            
            # Docstring module
            module_docstring = ast.get_docstring(tree)
            
            return {
                'has_module_docstring': module_docstring is not None,
                'functions_total': len(functions),
                'functions_documented': funcs_with_docs,
                'classes_total': len(classes),
                'classes_documented': classes_with_docs,
                'documentation_coverage': self._calc_coverage(
                    funcs_with_docs + classes_with_docs,
                    len(functions) + len(classes)
                ),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calc_coverage(self, documented: int, total: int) -> float:
        """Calcule le pourcentage de couverture"""
        if total == 0:
            return 100.0
        return round((documented / total) * 100, 2)
    
    def calculate_complexity(self, code: str) -> Dict:
        """
        Calcule la complexité cyclomatique (McCabe)
        
        Args:
            code: Code source Python
            
        Returns:
            Dict: Métriques de complexité
        """
        try:
            tree = ast.parse(code)
            
            complexities = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_function_complexity(node)
                    complexities.append({
                        'function': node.name,
                        'complexity': complexity,
                        'line': node.lineno
                    })
            
            if not complexities:
                avg_complexity = 0
                max_complexity = 0
            else:
                avg_complexity = sum(c['complexity'] for c in complexities) / len(complexities)
                max_complexity = max(c['complexity'] for c in complexities)
            
            return {
                'average_complexity': round(avg_complexity, 2),
                'max_complexity': max_complexity,
                'functions_analyzed': len(complexities),
                'complex_functions': [c for c in complexities if c['complexity'] > 10],
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """
        Calcule la complexité cyclomatique d'une fonction
        Formule simplifiée: 1 + nombre de points de décision
        """
        complexity = 1
        
        for node in ast.walk(func_node):
            # Points de décision
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def full_analysis(self, file_path: str, code: str) -> Dict:
        """
        Analyse complète: Pylint + syntaxe + docstrings + complexité
        
        Args:
            file_path: Chemin du fichier
            code: Code source
            
        Returns:
            Dict: Résultats complets
        """
        results = {
            'file': file_path,
            'timestamp': None,
            'pylint': self.run_pylint(file_path),
            'syntax': self.analyze_syntax(code, file_path),
            'docstrings': self.check_docstrings(code),
            'complexity': self.calculate_complexity(code)
        }
        
        # Score global (moyenne pondérée)
        scores = []
        if results['pylint'].get('score'):
            scores.append(results['pylint']['score'])
        if results['syntax'].get('valid_syntax'):
            scores.append(10.0)
        if results['docstrings'].get('documentation_coverage'):
            scores.append(results['docstrings']['documentation_coverage'] / 10)
        
        results['global_score'] = round(sum(scores) / len(scores) if scores else 0, 2)
        
        return results
    
    def generate_report(self, analysis: Dict) -> str:
        """
        Génère un rapport texte lisible
        
        Args:
            analysis: Résultat de full_analysis()
            
        Returns:
            str: Rapport formaté
        """
        report = []
        report.append(f"📊 RAPPORT D'ANALYSE: {analysis['file']}")
        report.append("=" * 60)
        
        # Score global
        report.append(f"\n🎯 Score Global: {analysis['global_score']}/10")
        
        # Pylint
        if 'score' in analysis['pylint']:
            report.append(f"\n📝 Pylint Score: {analysis['pylint']['score']}/10")
            report.append(f"   - Erreurs: {analysis['pylint']['error_count']}")
            report.append(f"   - Warnings: {analysis['pylint']['warning_count']}")
        
        # Syntaxe
        syntax_ok = "✅" if analysis['syntax'].get('valid_syntax') else "❌"
        report.append(f"\n{syntax_ok} Syntaxe: {'Valide' if analysis['syntax'].get('valid_syntax') else 'Invalide'}")
        
        # Docstrings
        doc_cov = analysis['docstrings'].get('documentation_coverage', 0)
        report.append(f"\n📚 Documentation: {doc_cov}%")
        
        # Complexité
        if 'average_complexity' in analysis['complexity']:
            report.append(f"\n🔧 Complexité moyenne: {analysis['complexity']['average_complexity']}")
            if analysis['complexity']['complex_functions']:
                report.append(f"   ⚠️ Fonctions complexes (>10): {len(analysis['complexity']['complex_functions'])}")
        
        return "\n".join(report)


# Test unitaire
if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    
    # Test code
    test_code = '''
def hello():
    """Dit bonjour"""
    print("Hello")

def complex_function(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    print(i)
    '''
    
    # Analyse syntaxe
    syntax_result = analyzer.analyze_syntax(test_code)
    print("Syntaxe:", syntax_result)
    
    # Analyse docstrings
    doc_result = analyzer.check_docstrings(test_code)
    print("Docstrings:", doc_result)
    
    # Complexité
    complexity_result = analyzer.calculate_complexity(test_code)
    print("Complexité:", complexity_result)