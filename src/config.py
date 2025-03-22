from pathlib import Path

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = Path('credentials/ankisync-service-account.json')
SPREADSHEET_ID = '1rBjRdlZ2HvswqsQ5gT_LECK4Zi6_aKuMhY919yTw89U'
RANGE_NAME = 'Sheet1!A:D'

# API endpoints
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
ANKI_CONNECT_ENDPOINT = "http://localhost:8765"

# File paths
BACKUP_FILE = Path('processed_rows.json')
LOG_FILE = Path('logs/processing.log')
