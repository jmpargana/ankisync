# Translation Project

A Python application to read multilingual data from Google Sheets, process it with Ollama's Mixtral model, add results to Anki via AnkiConnect, and delete processed rows.

## Setup

1. Install dependencies

```sh
pip install -r requirements.txt
```


2. Set up Google Sheets API credentials:
- Create a project in Google Cloud Console.
- Enable the Google Sheets API.
- Download credentials and save as `credentials/credentials.json`.
- Share your Google Sheet with the service account email.

3. Update configuration in `src/config.py`:
- Set `SPREADSHEET_ID` to your Google Sheet ID.
- Adjust other settings as needed.

4. Run the application:

```sh
python src/main.py
```

## Structure

- `src/config.py`: Configuration settings.
- `src/models/`: Data models (dataclasses).
- `src/clients/`: API clients for Google Sheets, Ollama, and AnkiConnect.
- `src/processor/`: Main processing logic.
- `src/main.py`: Entry point.
