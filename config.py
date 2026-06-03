import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL") or USER_EMAIL
ZOTERO_USER_ID = os.getenv("ZOTERO_USER_ID")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# 도커 컴포즈가 11개의 봇마다 다르게 주입해 주는 분과별 고유 이름표들
BOT_NAME = os.getenv("BOT_NAME", "general")
BOT_KOR_NAME = os.getenv("BOT_KOR_NAME", "일반 재활")
RUN_DAY = int(os.getenv("RUN_DAY", "1"))
ZOTERO_FOLDER_ID = os.getenv("ZOTERO_FOLDER_ID")
TARGET_ISSNS = os.getenv("TARGET_ISSNS", "")

# 봇 이름별로 DB와 로그 파일 완벽 독립 분리 생성
DB_FILE = f"history_{BOT_NAME}.db"
LOG_FILE = f"app_{BOT_NAME}.log"

current_year = datetime.now().year
# 노이즈를 덮기 위해 N수를 180편으로 설정
PERIODS = [
    {"label": f"[{BOT_KOR_NAME}] 최신 트렌드 발굴 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 50},
    {"label": f"[{BOT_KOR_NAME}] 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 70},
    {"label": f"[{BOT_KOR_NAME}] 클래식 족보 (과거 8~15년)", "start": current_year - 14, "end": current_year - 7, "top_n": 60}
]
