import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SHEET_CLICKS = "clicks"
SHEET_FEEDBACK = "feedback"


def _get_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_json = os.getenv("GOOGLE_CREDS")
        if not creds_json:
            logger.warning("GOOGLE_CREDS не ўсталяваны")
            return None
        creds_json_clean = creds_json.strip().strip('"').strip("'")
# Калі Railway перадаў з сапраўднымі \n унутры радкоў JSON
        if '\n' in creds_json_clean and 'BEGIN PRIVATE KEY' in creds_json_clean:
    # Замяняем сапраўдныя пераносы ўнутры значэнняў на \n
            import re
            creds_json_clean = re.sub(r'(?<=[^\\])\n', '\\n', creds_json_clean)
        creds_dict = json.loads(creds_json_clean)
        logger.info(f"project_id: {creds_dict.get('project_id')}, email: {creds_dict.get('client_email')}")
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        logger.info("gspread client створаны паспяхова")
        return client
    except Exception as e:
        logger.warning(f"Google Sheets не падключаны: {e}")
        return None


def log_click(user_id: int, section_key: str, section_name: str):
    try:
        client = _get_client()
        if not client:
            return
        spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
        logger.info(f"SPREADSHEET_ID: '{spreadsheet_id}' len={len(spreadsheet_id)}")
        sheet = client.open_by_key(spreadsheet_id).worksheet(SHEET_CLICKS)
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(user_id),
            section_key,
            section_name,
        ])
    except Exception as e:
        logger.warning(f"log_click памылка: {e}")


def log_feedback(user_id: int, section_key: str, rating: str, text: str = ""):
    try:
        client = _get_client()
        if not client:
            return
        spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
        sheet = client.open_by_key(spreadsheet_id).worksheet(SHEET_FEEDBACK)
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(user_id),
            section_key,
            rating,
            text,
        ])
    except Exception as e:
        logger.warning(f"log_feedback памылка: {e}")


def setup_headers():
    try:
        client = _get_client()
        if not client:
            print("GOOGLE_CREDS не ўсталяваны")
            return
        spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
        spreadsheet = client.open_by_key(spreadsheet_id)
        clicks = spreadsheet.worksheet(SHEET_CLICKS)
        clicks.update("A1:D1", [["timestamp", "user_id", "section_key", "section_name"]])
        feedback = spreadsheet.worksheet(SHEET_FEEDBACK)
        feedback.update("A1:E1", [["timestamp", "user_id", "section_key", "rating", "text"]])
        print("Загалоўкі дададзены")
    except Exception as e:
        print(f"Памылка: {e}")


if __name__ == "__main__":
    setup_headers()
