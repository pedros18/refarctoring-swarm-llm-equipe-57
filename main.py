#point d'entre du refactoring llm.
#systeme 3-agents pour la maintenance du code python...
import argparse
import sys
import os
from dotenv import load_dotenv

from src.utils.logger import log_experiment, ActionType
from src.orchestrator import RefactoringOrchestrator

# Charger les variables d'environnement
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="refactoring swarm - systeme de maintenance automatisee du code python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
exemples d'utilisation:
  python main.py --target_dir "./sandbox/test_local"
  python main.py --target_dir "./sandbox/dataset_inconnu" --model "gemini-1.5-flash"
        """
    )
    parser.add_argument(
        "--target_dir", 
        type=str, 
        required=True,
        help="Chemin vers le dossier contenant le code à refactorer"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="google/gemini-2.0-flash-001",
        help="Modèle LLM à utiliser via OpenRouter (défaut: google/gemini-2.0-flash-001)"
    )
    
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"dossier {args.target_dir} mkch")
        sys.exit(1)

    if not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY mkch. ")
        sys.exit(1)

    #logger
    log_experiment(
        agent_name="System",
        model_used="google/gemini-2.0-flash-001",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Démarrage du Refactoring Swarm sur {args.target_dir}",
            "output_response": "Initialisation...",
            "target_dir": args.target_dir,
            "model": args.model
        },
        status="SUCCESS"
    )

    #orchestrateur
    orchestrator = RefactoringOrchestrator(
        target_dir=args.target_dir,
        model_name=args.model
    )
    
    try:
        result = orchestrator.run()
        
        #end
        log_experiment(
            agent_name="System",
            model_used="google/gemini-2.0-flash-001",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Fin du Refactoring Swarm",
                "output_response": f"Traitement terminé: {result['stats']}",
                "stats": result["stats"]
            },
            status="SUCCESS" if result["success"] else "FAILURE"
        )
        
        if result["success"]:
            print("done!")
            sys.exit(0)
        else:
            print("not done yet!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\ncontrol c")
        sys.exit(130)
    except Exception as e:
        print(f"eror: {e}")
        log_experiment(
            agent_name="System",
            model_used="google/gemini-2.0-flash-001",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Erreur fatale",
                "output_response": str(e),
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()