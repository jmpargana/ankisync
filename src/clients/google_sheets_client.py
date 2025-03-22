import logging
from typing import List
from pathlib import Path
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
from models.language_entry import WordEntry
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    def __init__(self, creds_file: Path, scopes: List[str], spreadsheet_id: str, range_name: str):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service = self._get_service(creds_file, scopes)

    def _get_service(self, creds_file: Path, scopes: List[str]):
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=scopes)
        return build('sheets', 'v4', credentials=credentials)

    def read_sheet(self) -> List[WordEntry]:
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()

            values = result.get('values', [])
            if not values:
                logger.warning("No data found in Google Sheet")
                return []

            entries = []
            languages = ["german", "turkish", "russian", "english"]
            for row in values[0:]:  # Skip header row
                while len(row) < len(languages):
                    row.append("")
                row_entries = [
                    WordEntry(word=word.strip(), language=lang)
                    for word, lang in zip(row, languages)
                    if word.strip()
                ]
                if row_entries:
                    entries.append(*row_entries)
            return entries

        except Exception as e:
            logger.error(f"Failed to read from Google Sheet: {str(e)}")
            raise

    def delete_rows(self, row_indices: List[int]):
        try:
            row_indices = sorted(row_indices, reverse=True)
            batch_update_request = {
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": 0,
                                "dimension": "ROWS",
                                "startIndex": idx,
                                "endIndex": idx + 1
                            }
                        }
                    }
                    for idx in row_indices
                ]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=batch_update_request
            ).execute()
            logger.info(f"Deleted {len(row_indices)} rows from Google Sheet")
        except Exception as e:
            logger.error(f"Failed to delete rows from Google Sheet: {str(e)}")
            raise
