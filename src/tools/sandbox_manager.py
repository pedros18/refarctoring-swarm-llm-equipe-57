"""
Sandbox Manager - Gestion sécurisée de l'environnement d'exécution
Author: Toolsmith
Description: Isolation et protection pour l'exécution de code non fiable
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
import hashlib
import time


class SandboxManager:
    """Gestionnaire de sandbox pour isolation sécurisée"""
    
    def __init__(self, base_sandbox: str = "./sandbox"):
        """
        Initialise le gestionnaire de sandbox
        
        Args:
            base_sandbox: Répertoire racine du sandbox
        """
        self.base_sandbox = Path(base_sandbox).resolve()
        self.base_sandbox.mkdir(parents=True, exist_ok=True)
        
        # Sous-dossiers du sandbox
        self.work_dir = self.base_sandbox / "work"
        self.backup_dir = self.base_sandbox / "backups"
        self.temp_dir = self.base_sandbox / "temp"
        
        # Créer la structure
        self._init_sandbox_structure()
        
        # Tracking
        self.current_session_id = None
        self.session_history = []
    
    def _init_sandbox_structure(self):
        """Crée la structure du sandbox"""
        self.work_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Créer un fichier .gitkeep pour garder les dossiers vides
        for directory in [self.work_dir, self.backup_dir, self.temp_dir]:
            gitkeep = directory / ".gitkeep"
            gitkeep.touch(exist_ok=True)
    
    def create_session(self, session_name: Optional[str] = None) -> str:
        """
        Crée une nouvelle session de travail isolée
        
        Args:
            session_name: Nom de la session (généré si None)
            
        Returns:
            str: ID de la session
        """
        if session_name is None:
            # Générer un ID unique basé sur timestamp
            timestamp = int(time.time() * 1000)
            session_name = f"session_{timestamp}"
        
        self.current_session_id = session_name
        
        # Créer le dossier de session
        session_path = self.work_dir / session_name
        session_path.mkdir(exist_ok=True)
        
        # Enregistrer dans l'historique
        self.session_history.append({
            'id': session_name,
            'created_at': time.time(),
            'path': str(session_path)
        })
        
        print(f"✅ Session créée: {session_name}")
        return session_name
    
    def get_session_path(self, session_id: Optional[str] = None) -> Path:
        """
        Obtient le chemin d'une session
        
        Args:
            session_id: ID de la session (utilise current si None)
            
        Returns:
            Path: Chemin du dossier de session
        """
        if session_id is None:
            session_id = self.current_session_id
        
        if session_id is None:
            raise ValueError("Aucune session active")
        
        return self.work_dir / session_id
    
    def import_code(self, source_path: str, session_id: Optional[str] = None) -> bool:
        """
        Importe du code externe dans le sandbox
        
        Args:
            source_path: Chemin du code source
            session_id: ID de session (utilise current si None)
            
        Returns:
            bool: True si succès
        """
        try:
            source = Path(source_path).resolve()
            
            if not source.exists():
                print(f"❌ Source inexistante: {source_path}")
                return False
            
            # Obtenir le chemin de session
            session_path = self.get_session_path(session_id)
            
            # Copier selon le type
            if source.is_file():
                dest = session_path / source.name
                shutil.copy2(source, dest)
                print(f"✅ Fichier copié: {source.name}")
            else:
                # Copier le contenu du répertoire
                for item in source.iterdir():
                    if item.is_file():
                        shutil.copy2(item, session_path / item.name)
                    else:
                        shutil.copytree(item, session_path / item.name, dirs_exist_ok=True)
                print(f"✅ Dossier copié: {source.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur import: {e}")
            return False
    
    def create_backup(self, session_id: Optional[str] = None, tag: str = "auto") -> Optional[str]:
        """
        Crée un backup de la session actuelle
        
        Args:
            session_id: ID de session
            tag: Tag pour identifier le backup
            
        Returns:
            str: Chemin du backup ou None
        """
        try:
            session_path = self.get_session_path(session_id)
            
            if not session_path.exists():
                print("⚠️ Session inexistante")
                return None
            
            # Créer le nom du backup
            timestamp = int(time.time())
            backup_name = f"{session_id or self.current_session_id}_{tag}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Copier la session
            shutil.copytree(session_path, backup_path)
            
            print(f"💾 Backup créé: {backup_name}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Erreur backup: {e}")
            return None
    
    def restore_backup(self, backup_name: str, session_id: Optional[str] = None) -> bool:
        """
        Restaure un backup dans la session
        
        Args:
            backup_name: Nom du backup
            session_id: ID de session cible
            
        Returns:
            bool: True si succès
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                print(f"❌ Backup inexistant: {backup_name}")
                return False
            
            session_path = self.get_session_path(session_id)
            
            # Supprimer la session actuelle
            if session_path.exists():
                shutil.rmtree(session_path)
            
            # Restaurer le backup
            shutil.copytree(backup_path, session_path)
            
            print(f"✅ Backup restauré: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur restauration: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """
        Liste tous les backups disponibles
        
        Returns:
            List[Dict]: Liste des backups avec métadonnées
        """
        backups = []
        
        for backup_path in self.backup_dir.iterdir():
            if backup_path.is_dir() and not backup_path.name.startswith('.'):
                # Parser le nom (session_tag_timestamp)
                parts = backup_path.name.split('_')
                
                backups.append({
                    'name': backup_path.name,
                    'path': str(backup_path),
                    'size_mb': self._get_dir_size(backup_path) / (1024 * 1024),
                    'created': backup_path.stat().st_ctime
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def _get_dir_size(self, path: Path) -> int:
        """Calcule la taille d'un répertoire en octets"""
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
    
    def clean_session(self, session_id: Optional[str] = None) -> bool:
        """
        Nettoie une session (supprime tous les fichiers)
        
        Args:
            session_id: ID de session
            
        Returns:
            bool: True si succès
        """
        try:
            session_path = self.get_session_path(session_id)
            
            if session_path.exists():
                shutil.rmtree(session_path)
                session_path.mkdir(exist_ok=True)
                print(f"🧹 Session nettoyée: {session_id or self.current_session_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur nettoyage: {e}")
            return False
    
    def clean_all_temp(self) -> bool:
        """
        Nettoie tous les fichiers temporaires
        
        Returns:
            bool: True si succès
        """
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
                print("🧹 Fichiers temporaires supprimés")
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur nettoyage temp: {e}")
            return False
    
    def get_sandbox_stats(self) -> Dict:
        """
        Obtient les statistiques du sandbox
        
        Returns:
            Dict: Statistiques (taille, nombre de fichiers, etc.)
        """
        stats = {
            'total_size_mb': self._get_dir_size(self.base_sandbox) / (1024 * 1024),
            'sessions': len(list(self.work_dir.iterdir())),
            'backups': len(list(self.backup_dir.iterdir())),
            'current_session': self.current_session_id,
            'work_size_mb': self._get_dir_size(self.work_dir) / (1024 * 1024),
            'backup_size_mb': self._get_dir_size(self.backup_dir) / (1024 * 1024)
        }
        
        return stats
    
    def validate_session(self, session_id: Optional[str] = None) -> Dict:
        """
        Valide l'état d'une session
        
        Args:
            session_id: ID de session
            
        Returns:
            Dict: État de validation
        """
        try:
            session_path = self.get_session_path(session_id)
            
            if not session_path.exists():
                return {
                    'valid': False,
                    'error': 'Session inexistante'
                }
            
            # Compter les fichiers Python
            py_files = list(session_path.rglob('*.py'))
            
            # Vérifier les permissions
            readable = os.access(session_path, os.R_OK)
            writable = os.access(session_path, os.W_OK)
            
            return {
                'valid': True,
                'path': str(session_path),
                'python_files': len(py_files),
                'total_files': sum(1 for _ in session_path.rglob('*') if _.is_file()),
                'readable': readable,
                'writable': writable,
                'size_mb': self._get_dir_size(session_path) / (1024 * 1024)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def export_session(self, output_path: str, session_id: Optional[str] = None) -> bool:
        """
        Exporte une session vers un emplacement externe
        
        Args:
            output_path: Chemin de destination
            session_id: ID de session
            
        Returns:
            bool: True si succès
        """
        try:
            session_path = self.get_session_path(session_id)
            dest = Path(output_path).resolve()
            
            # Copier la session
            if dest.exists():
                shutil.rmtree(dest)
            
            shutil.copytree(session_path, dest)
            
            print(f"📤 Session exportée: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur export: {e}")
            return False


# Test unitaire
if __name__ == "__main__":
    manager = SandboxManager("./test_sandbox")
    
    # Test création session
    session_id = manager.create_session("test_session")
    print(f"Session créée: {session_id}")
    
    # Test backup
    backup = manager.create_backup(tag="initial")
    print(f"Backup: {backup}")
    
    # Test stats
    stats = manager.get_sandbox_stats()
    print(f"Stats: {stats}")
    
    # Test validation
    validation = manager.validate_session()
    print(f"Validation: {validation}")