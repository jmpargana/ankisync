import logging
import json
import time
from typing import List
from pathlib import Path
from models.translation_entry import TranslationEntry
from models.language_entry import WordEntry
from clients.google_sheets_client import GoogleSheetsClient
from clients.ollama_client import OllamaClient
from clients.anki_client import AnkiClient

logger = logging.getLogger(__name__)

PROMPTS = {
    'english': """Please explain the meaning of this word: {word}, alongside a few example sentences. If possible, include the translation to portuguese, including the same examples translated.""",
    'german': """Please explain what this word means: {word}, include some example sentences (in german) alongside their translations to english.""",
    'turkish': """Please explain what this word means: {word}, include some example sentences (in turkish) alongside their translations to english.""",
    'russian': """Please explain what this word means: {word}, include some example sentences (in russian) alongside their translations to english.""",
}

class TranslationProcessor:
    def __init__(
        self,
        sheet_entries: List[WordEntry],
        ollama_client: OllamaClient,
        anki_client: AnkiClient,
        backup_file: Path
    ):
        self.sheet_entries = sheet_entries
        self.ollama_client = ollama_client
        self.anki_client = anki_client
        self.backup_file = backup_file
        self.entries: List[TranslationEntry] = []
        self.successful_rows = set()

    def load_backup(self):
        if self.backup_file.exists():
            with open(self.backup_file, 'r') as f:
                self.successful_rows = set(json.load(f))

    def save_backup(self):
        with open(self.backup_file, 'w') as f:
            json.dump(list(self.successful_rows), f)

    def process_row(self, row_index: int, languages: WordEntry) -> TranslationEntry:
        entry = TranslationEntry(row_index=row_index, entry=languages)

        try:
            result = self.ollama_client.process(PROMPTS[entry.entry.language], entry.entry.word)
            entry.prompt_result = result

            if self.anki_client.add_note(entry):
                entry.anki_added = True
                self.successful_rows.add(row_index)
                self.save_backup()
            else:
                raise Exception("Anki addition failed")

        except Exception as e:
            entry.error = str(e)
            logger.error(f"Failed to process row {row_index}: {str(e)}")

        return entry

    def run(self, max_retries: int = 3) -> List[TranslationEntry]:
        self.load_backup()
        self.entries = []

        logger.debug(f"sheet_entries: {self.sheet_entries}")
        logger.debug(f"First entry type: {type(self.sheet_entries[0]) if self.sheet_entries else 'empty'}")

        for idx, languages in enumerate(self.sheet_entries):
            if idx in self.successful_rows:
                logger.info(f"Skipping already processed row {idx}")
                continue

            retries = 0
            while retries < max_retries:
                try:
                    entry = self.process_row(idx, languages)
                    self.entries.append(entry)
                    if entry.error:
                        logger.warning(f"Row {idx} failed permanently after {retries + 1} attempts")
                        break
                    break
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Max retries reached for row {idx}: {str(e)}")
                        self.entries.append(TranslationEntry(
                            row_index=idx,
                            entry=languages,
                            prompt_result="",
                            error=f"Max retries reached: {str(e)}"
                        ))
                    else:
                        logger.info(f"Retrying row {idx} (attempt {retries + 1}/{max_retries})")
                        time.sleep(2 ** retries)

        return self.entries

    def cleanup_sheet(self, google_sheets_client: GoogleSheetsClient):
        try:
            successful_indices = [entry.row_index for entry in self.entries if entry.anki_added]
            if successful_indices:
                adjusted_indices = [idx + 1 for idx in successful_indices]
                google_sheets_client.delete_rows(adjusted_indices)
                logger.info(f"Removed {len(successful_indices)} successful entries from sheet")
        except Exception as e:
            logger.error(f"Failed to cleanup sheet: {str(e)}")
