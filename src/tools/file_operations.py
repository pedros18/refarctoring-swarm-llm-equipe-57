"""
File Operations Tool - Secure file reading/writing with sandbox protection
Author: Toolsmith
Description: Gestion sécurisée des fichiers avec protection sandbox
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
import json


class FileOperations:
    """Opérations fichiers sécurisées avec enforcement du sandbox"""
    
    def __init__(self, sandbox_root: str = "./sandbox"):
        """
        Initialise le gestionnaire de fichiers
        
        Args:
            sandbox_root: Chemin racine du sandbox (par défaut ./sandbox)
        """
        self.sandbox_root = Path(sandbox_root).resolve()
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        
    def _validate_path(self, file_path: str) -> Path:
        """
        ⚠️ SÉCURITÉ CRITIQUE: Valide que le chemin est dans le sandbox
        
        Args:
            file_path: Chemin du fichier à valider
            
        Returns:
            Path: Chemin validé et résolu
            
        Raises:
            ValueError: Si le chemin sort du sandbox
        """
        # Résoudre le chemin relatif au sandbox root (pas au CWD)
        # Si le chemin est absolu, on le garde tel quel, sinon on le résout depuis sandbox_root
        if Path(file_path).is_absolute():
            target = Path(file_path).resolve()
        else:
            target = (self.sandbox_root / file_path).resolve()
        
        # Vérifier que le chemin est dans le sandbox
        try:
            target.relative_to(self.sandbox_root)
        except ValueError:
            raise ValueError(
                f"⚠️ VIOLATION SÉCURITÉ: Le chemin '{file_path}' est en dehors du sandbox '{self.sandbox_root}'"
            )
        
        return target
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Lecture sécurisée d'un fichier
        
        Args:
            file_path: Chemin du fichier (relatif au sandbox)
            
        Returns:
            str ou None: Contenu du fichier ou None si erreur/inexistant
            
        Raises:
            ValueError: Si le chemin est en dehors du sandbox (violation sécurité)
        """
        try:
            safe_path = self._validate_path(file_path)
            
            if not safe_path.exists():
                print(f"⚠️ Fichier inexistant: {file_path}")
                return None
                
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except ValueError:
            # Re-raise security violations (ValueError from _validate_path)
            raise
        except Exception as e:
            print(f"❌ Erreur lecture {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Écriture sécurisée dans un fichier
        
        Args:
            file_path: Chemin du fichier (relatif au sandbox)
            content: Contenu à écrire
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            safe_path = self._validate_path(file_path)
            
            # Créer les dossiers parents si nécessaire
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fichier écrit: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur écriture {file_path}: {e}")
            return False
    
    def list_python_files(self, directory: str = ".") -> List[str]:
        """
        Liste tous les fichiers .py dans un répertoire (récursif)
        
        Args:
            directory: Répertoire à scanner (relatif au sandbox)
            
        Returns:
            List[str]: Liste des chemins de fichiers Python
        """
        try:
            safe_dir = self._validate_path(directory)
            
            python_files = []
            for py_file in safe_dir.rglob("*.py"):
                # Chemin relatif au sandbox
                rel_path = py_file.relative_to(self.sandbox_root)
                python_files.append(str(rel_path))
            
            return sorted(python_files)
            
        except Exception as e:
            print(f"❌ Erreur listage fichiers: {e}")
            return []
    
    def copy_to_sandbox(self, source_dir: str, dest_name: str = "work") -> bool:
        """
        Copie un répertoire externe dans le sandbox
        
        Args:
            source_dir: Répertoire source (peut être hors sandbox)
            dest_name: Nom du dossier destination dans sandbox
            
        Returns:
            bool: True si succès
        """
        try:
            source = Path(source_dir).resolve()
            
            if not source.exists():
                raise ValueError(f"Le répertoire source '{source_dir}' n'existe pas")
            
            dest = self.sandbox_root / dest_name
            
            # Supprimer l'existant si présent
            if dest.exists():
                shutil.rmtree(dest)
            
            # Copier
            shutil.copytree(source, dest)
            
            print(f"✅ Copié {source_dir} → {dest}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur copie vers sandbox: {e}")
            return False
    
    def get_file_stats(self, file_path: str) -> Optional[Dict]:
        """
        Obtenir les statistiques d'un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Dict: Stats (size, lines, etc.) ou None
        """
        try:
            safe_path = self._validate_path(file_path)
            
            if not safe_path.exists():
                return None
            
            content = self.read_file(file_path)
            
            return {
                'path': file_path,
                'size_bytes': safe_path.stat().st_size,
                'lines': len(content.splitlines()) if content else 0,
                'is_python': file_path.endswith('.py')
            }
            
        except Exception as e:
            print(f"❌ Erreur stats {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Suppression sécurisée d'un fichier
        
        Args:
            file_path: Chemin du fichier à supprimer
            
        Returns:
            bool: True si succès
        """
        try:
            safe_path = self._validate_path(file_path)
            
            if safe_path.exists():
                safe_path.unlink()
                print(f"🗑️ Fichier supprimé: {file_path}")
                return True
            else:
                print(f"⚠️ Fichier inexistant: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur suppression {file_path}: {e}")
            return False
    
    def backup_file(self, file_path: str) -> Optional[str]:
        """
        Crée une sauvegarde d'un fichier avant modification
        
        Args:
            file_path: Chemin du fichier à sauvegarder
            
        Returns:
            str: Chemin du backup ou None
        """
        try:
            safe_path = self._validate_path(file_path)
            
            if not safe_path.exists():
                return None
            
            # Créer le nom du backup
            backup_path = safe_path.with_suffix(safe_path.suffix + '.backup')
            
            shutil.copy2(safe_path, backup_path)
            
            print(f"💾 Backup créé: {backup_path.name}")
            return str(backup_path.relative_to(self.sandbox_root))
            
        except Exception as e:
            print(f"❌ Erreur backup {file_path}: {e}")
            return None


# Test unitaire
if __name__ == "__main__":
    # Test des opérations de base
    fo = FileOperations("./sandbox_test")
    
    # Test écriture
    fo.write_file("test.py", "print('Hello World')")
    
    # Test lecture
    content = fo.read_file("test.py")
    print(f"Contenu lu: {content}")
    
    # Test liste fichiers
    files = fo.list_python_files()
    print(f"Fichiers Python: {files}")
    
    # Test sécurité (doit échouer)
    try:
        fo.read_file("../../etc/passwd")
    except ValueError as e:
        print(f"✅ Sécurité OK: {e}")