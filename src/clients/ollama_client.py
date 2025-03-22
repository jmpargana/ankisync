import logging
import requests

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def process(self, prompt: str, word: str) -> str:
        logger.info(f"Calling Ollama with {word}")
        try:
            payload = {
                "model": "mixtral",
                "prompt": prompt.format(word=word),
                "stream": False
            }
            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Ollama call failed for word {word}: {str(e)}")
            raise
