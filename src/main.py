import logging
from config import (
    SCOPES, CREDS_FILE, SPREADSHEET_ID, RANGE_NAME,
    OLLAMA_ENDPOINT, ANKI_CONNECT_ENDPOINT, LOG_FILE, BACKUP_FILE
)
from clients.google_sheets_client import GoogleSheetsClient
from clients.ollama_client import OllamaClient
from clients.anki_client import AnkiClient
from processor.translation_processor import TranslationProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    sheets_client = GoogleSheetsClient(CREDS_FILE, SCOPES, SPREADSHEET_ID, RANGE_NAME)

    sheet_entries = sheets_client.read_sheet()

    logger.info(f"Read all of these entries {sheet_entries}")

    ollama_client = OllamaClient(OLLAMA_ENDPOINT)
    anki_client = AnkiClient(ANKI_CONNECT_ENDPOINT)

    processor = TranslationProcessor(sheet_entries, ollama_client, anki_client, BACKUP_FILE)
    results = processor.run()

    processor.cleanup_sheet(sheets_client)

    successful = sum(1 for entry in results if entry.anki_added)
    failed = len(results) - successful
    logger.info(f"Processing complete: {successful} successful, {failed} failed")
    for entry in results:
        if entry.error:
            logger.warning(f"Failed entry {entry.row_index}: {entry.error}")

if __name__ == "__main__":
    main()
