#code de base pour tous les agents du Refactoring Swarm.
import os
import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.utils.logger import log_experiment, ActionType


class BaseAgent(ABC):
   
    API_DELAY = 2  
    MAX_RETRIES = 3
    RETRY_DELAY = 30  #delay
    
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, name: str, model_name: str = "google/gemini-2.0-flash-001"):
 
        self.name = name
        self.model_name = model_name
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY non trouve dans les variables d'environnement")
        return api_key
    
    def call_llm(self, prompt: str, system_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/refactoring-swarm",
            "X-Title": "Refactoring Swarm"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                time.sleep(self.API_DELAY)
                
                response = requests.post(
                    self.OPENROUTER_API_URL,
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                
                elif response.status_code == 429:
                    if attempt < self.MAX_RETRIES - 1:
                        print(f" limit. Attente de {self.RETRY_DELAY}s ({attempt + 1}/{self.MAX_RETRIES})")
                        time.sleep(self.RETRY_DELAY)
                        continue
                    return f"error: rate limit depass apres {self.MAX_RETRIES} tries"
                
                else:
                    error_msg = response.json().get("error", {}).get("message", response.text)
                    return f"eror: {response.status_code} - {error_msg}"
                    
            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    print(f"timeout essay ({attempt + 1}/{self.MAX_RETRIES})")
                    continue
                return "error: timeout apres plusieurs tries"
                
            except Exception as e:
                return f"error: {str(e)}"
        
        return "eror: nombre maximum de tries arrived"
    
    def log_action(self, action: ActionType, details: Dict[str, Any], status: str) -> None:
        log_experiment(
            agent_name=self.name,
            model_used=self.model_name,
            action=action,
            details=details,
            status=status
        )
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        pass
