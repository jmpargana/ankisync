from dataclasses import dataclass
from typing import Dict, Optional
from models.language_entry import WordEntry

@dataclass
class TranslationEntry:
    row_index: int
    entry: WordEntry
    prompt_result: str = ""
    anki_added: bool = False
    error: Optional[str] = None
