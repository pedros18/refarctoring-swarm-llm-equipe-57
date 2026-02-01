"""
Toolsmith Package - API Interne pour Refactoring Swarm
Author: Toolsmith Team
Version: 1.0.0
Description: Ensemble complet d'outils pour manipulation sécurisée de code
"""

from .file_operations import FileOperations
from .code_analyzer import CodeAnalyzer
from .test_runner import TestRunner
from .sandbox_manager import SandboxManager
from .llm_client import LlamaClient

__all__ = [
    'FileOperations',
    'CodeAnalyzer',
    'TestRunner',
    'SandboxManager',
    'LlamaClient'
]

__version__ = '1.0.0'
__author__ = 'Toolsmith Team'


# Fonction utilitaire pour initialiser tous les outils
def init_all_tools(sandbox_path: str = "./sandbox", llm_provider: str = "replicate"):
    """
    Initialise tous les outils en une seule fois
    
    Args:
        sandbox_path: Chemin du sandbox
        llm_provider: Provider LLM à utiliser
        
    Returns:
        dict: Dictionnaire avec tous les outils initialisés
    """
    return {
        'file_ops': FileOperations(sandbox_path),
        'analyzer': CodeAnalyzer(),
        'test_runner': TestRunner(),
        'sandbox': SandboxManager(sandbox_path),
        'llm': LlamaClient(provider=llm_provider)
    }


# Messages d'aide pour les autres membres de l'équipe
USAGE_GUIDE = """
📖 GUIDE D'UTILISATION - TOOLSMITH API

1️⃣ FILE OPERATIONS (Lecture/Écriture sécurisée)
   from src.tools import FileOperations
   
   fo = FileOperations("./sandbox")
   content = fo.read_file("code.py")
   fo.write_file("fixed.py", new_content)
   files = fo.list_python_files()

2️⃣ CODE ANALYZER (Analyse Pylint + Complexité)
   from src.tools import CodeAnalyzer
   
   analyzer = CodeAnalyzer()
   results = analyzer.run_pylint("file.py")
   full_analysis = analyzer.full_analysis("file.py", code)
   report = analyzer.generate_report(full_analysis)

3️⃣ TEST RUNNER (Exécution Pytest)
   from src.tools import TestRunner
   
   runner = TestRunner()
   results = runner.run_pytest("tests/")
   report = runner.generate_test_report()

4️⃣ SANDBOX MANAGER (Isolation sécurisée)
   from src.tools import SandboxManager
   
   sandbox = SandboxManager()
   session_id = sandbox.create_session()
   sandbox.import_code("./messy_code", session_id)
   sandbox.create_backup(tag="before_fix")

5️⃣ LLM CLIENT (API Llama haute performance)
   from src.tools import LlamaClient
   
   llm = LlamaClient(provider="replicate")
   response = llm.generate(
       prompt="Corrige ce code: ...",
       system_prompt="Tu es un expert Python"
   )

📦 INIT RAPIDE (Tous les outils en une fois)
   from src.tools import init_all_tools
   
   tools = init_all_tools(sandbox_path="./sandbox")
   # Accès: tools['file_ops'], tools['analyzer'], etc.

⚠️ SÉCURITÉ
   - Tous les fichiers sont validés dans le sandbox
   - Impossible d'écrire en dehors de ./sandbox
   - Les backups sont automatiques
   
💡 POUR LES AGENTS
   Ces outils sont conçus pour être appelés par vos agents.
   Exemple dans un agent:
   
   from src.tools import FileOperations, LlamaClient
   
   def analyze_and_fix(file_path):
       fo = FileOperations()
       llm = LlamaClient()
       
       # Lire
       code = fo.read_file(file_path)
       
       # Analyser avec LLM
       response = llm.generate(f"Analyse: {code}")
       
       # Écrire le fix
       fo.write_file(file_path, response['response'])
"""


def print_usage():
    """Affiche le guide d'utilisation"""
    print(USAGE_GUIDE)


# Test d'intégration
if __name__ == "__main__":
    print("🛠️ TOOLSMITH PACKAGE - Test d'intégration\n")
    
    # Test init
    try:
        tools = init_all_tools()
        print("✅ Tous les outils initialisés avec succès!")
        print(f"   - FileOperations: {type(tools['file_ops']).__name__}")
        print(f"   - CodeAnalyzer: {type(tools['analyzer']).__name__}")
        print(f"   - TestRunner: {type(tools['test_runner']).__name__}")
        print(f"   - SandboxManager: {type(tools['sandbox']).__name__}")
        print(f"   - LlamaClient: {type(tools['llm']).__name__}")
        
        print("\n" + "="*60)
        print_usage()
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")