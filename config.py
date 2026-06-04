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

BOT_NAME = os.getenv("BOT_NAME", "general")
BOT_KOR_NAME = os.getenv("BOT_KOR_NAME", "일반 재활")
RUN_MONTH = int(os.getenv("RUN_MONTH", "1"))
ZOTERO_FOLDER_ID = os.getenv("ZOTERO_FOLDER_ID")
TARGET_ISSNS = os.getenv("TARGET_ISSNS", "")

DB_FILE = f"history_{BOT_NAME}.db"
LOG_FILE = f"app_{BOT_NAME}.log"

current_year = datetime.now().year

# 🚀 12월 AI 봇 전용 세팅 (기간 단축 및 전용 AI 검색 키워드)
if BOT_NAME == "ai":
    PERIODS = [
        {"label": f"[{BOT_KOR_NAME}] 최신 AI 융합 트렌드 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 80},
        {"label": f"[{BOT_KOR_NAME}] AI 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 100}
    ]
    # 논문의 제목이나 초록에 아래 단어가 들어간 논문만 필터링합니다
    AI_SEARCH_KEYWORDS = '"artificial intelligence"|"machine learning"|"deep learning"|"language model"|"chatgpt"|"computer vision"|"natural language processing"'
else:
    # 🩺 기존 1~11월 분과 봇 기본 세팅
    PERIODS = [
        {"label": f"[{BOT_KOR_NAME}] 최신 트렌드 발굴 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 50},
        {"label": f"[{BOT_KOR_NAME}] 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 70},
        {"label": f"[{BOT_KOR_NAME}] 클래식 족보 (과거 8~15년)", "start": current_year - 14, "end": current_year - 7, "top_n": 60}
    ]
    AI_SEARCH_KEYWORDS = ""
