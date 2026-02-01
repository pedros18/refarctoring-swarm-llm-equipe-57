"""
LlamaClient - Client unifié pour Llama via OpenRouter
Author: Toolsmith
Description: Client haute performance pour API Llama (OpenRouter uniquement)
"""

import os
from typing import Optional, Dict
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class LlamaClient:
    """
    Client pour OpenRouter uniquement
    """
    
    def __init__(
        self,
        provider: str = "openrouter",
        model: str = "openai/gpt-4o-mini",  # Modèle 
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        if provider != "openrouter":
            raise ValueError("Seul le provider 'openrouter' est supporté maintenant")
        
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self._init_openrouter()
    
    def _init_openrouter(self):
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY manquant dans .env")
            self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            print("✅ OpenRouter initialisé")
        except ImportError:
            raise ImportError("pip install openai")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict:
        start_time = time.time()
        for attempt in range(max_retries):
            try:
                result = self._generate_openrouter(prompt, system_prompt)
                result['time'] = time.time() - start_time
                result['model'] = self.model
                result['provider'] = self.provider
                self.total_calls += 1
                self.total_tokens += result.get('usage', {}).get('total_tokens', 0)
                return result
            except Exception as e:
                print(f"⚠️ Tentative {attempt+1}/{max_retries} échouée: {e}")
                if attempt == max_retries - 1:
                    return {'response': None, 'error': str(e), 'time': time.time() - start_time}
                time.sleep(2 ** attempt)
    
    def _generate_openrouter(self, prompt: str, system_prompt: Optional[str]) -> Dict:
        messages = [{"role":"system","content":system_prompt}] if system_prompt else []
        messages.append({"role":"user","content":prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return {
            'response': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }
    
    def get_stats(self) -> Dict:
        return {
            'provider': self.provider,
            'model': self.model,
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'avg_tokens_per_call': self.total_tokens / self.total_calls if self.total_calls > 0 else 0
        }
    
    def reset_stats(self):
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0


# -------------------------
# Script de test principal
# -------------------------
if __name__ == "__main__":
    print("🧪 Test LlamaClient OpenRouter\n")
    
    # Lead Dev peut simplement faire:
    llm = LlamaClient()  # modèle refactoring-swarm-v1 déjà utilisé
    
    prompt = "Explique la complexité cyclomatique en une phrase."
    system_prompt = "Tu es un expert en génie logiciel."
    
    result = llm.generate(prompt, system_prompt)
    
    print("\n✅ Réponse:", result['response'])
    print("⏱ Temps:", f"{result['time']:.2f}s")
    print("📊 Usage:", result.get('usage', {}))
    print("📈 Stats:", llm.get_stats())
