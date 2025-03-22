import logging
import requests
from models.translation_entry import TranslationEntry

logger = logging.getLogger(__name__)

class AnkiClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def add_note(self, entry: TranslationEntry) -> bool:
        try:
            payload = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": entry.entry.language,
                        "modelName": "Basic",
                        "fields": {
                            "Front": entry.entry.word,
                            "Back": entry.prompt_result
                        },
                        "tags": ["auto-generated"]
                    }
                }
            }
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.json().get("result") is not None
        except Exception as e:
            logger.error(f"AnkiConnect call failed for word {entry.entry.word}: {str(e)}")
            raise
