from dataclasses import dataclass

@dataclass
class LanguageEntry:
    german: str
    turkish: str
    russian: str
    english: str

@dataclass
class WordEntry:
    word: str
    language: str
