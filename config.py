import os
from datetime import datetime
from dotenv import load_dotenv

# ==============================================================
# 📂 [완벽 폴더 구조 정리] 데이터와 로그를 전용 폴더로 격리
# ==============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, ".env"))

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

# 🚀 분리된 폴더로 파일 생성 경로 지정
DB_FILE = os.path.join(DATA_DIR, f"history_{BOT_NAME}.db")
LOG_FILE = os.path.join(LOGS_DIR, f"app_{BOT_NAME}.log")
current_year = datetime.now().year

# ==============================================================
# 🎯 봇별 공식 탐색 대상 저널 DB (Target Journal Pool)
# ==============================================================
JOURNALS_DB = {
    "general": [
        {"tier": "JCR Q1", "name": "Archives of Physical Medicine and Rehabilitation", "issn": "0003-9993"},
        {"tier": "JCR Q1", "name": "Clinical Rehabilitation", "issn": "0269-2155"},
        {"tier": "JCR Q1", "name": "American Journal of Physical Medicine & Rehabilitation", "issn": "0894-9115"},
        {"tier": "JCR Q1", "name": "Journal of Rehabilitation Medicine", "issn": "1650-1977"},
        {"tier": "JCR Q1", "name": "European Journal of Physical and Rehabilitation Medicine", "issn": "1973-9087"},
        {"tier": "JCR Q1", "name": "Disability and Rehabilitation", "issn": "0963-8288"},
        {"tier": "JCR Q2", "name": "PM&R", "issn": "1934-1482"},
        {"tier": "KCI/ESCI", "name": "Annals of Rehabilitation Medicine", "issn": "2234-0645"}
    ],
    "neuro": [
        {"tier": "JCR Q1", "name": "Stroke", "issn": "0039-2499"},
        {"tier": "JCR Q1", "name": "Neurorehabilitation and Neural Repair", "issn": "1545-9683"},
        {"tier": "JCR Q1", "name": "Journal of NeuroEngineering and Rehabilitation", "issn": "1743-0003"},
        {"tier": "JCR Q2", "name": "Topics in Stroke Rehabilitation", "issn": "1074-9357"}
    ],
    "sci": [
        {"tier": "JCR Q2", "name": "Spinal Cord", "issn": "1362-4393"},
        {"tier": "JCR Q3", "name": "The Journal of Spinal Cord Medicine", "issn": "1079-0268"},
        {"tier": "ESCI", "name": "Spinal Cord Series and Cases", "issn": "2058-6124"}
    ],
    "peds": [
        {"tier": "JCR Q1", "name": "Developmental Medicine & Child Neurology", "issn": "0012-1622"},
        {"tier": "JCR Q1", "name": "Physical & Occupational Therapy in Pediatrics", "issn": "0194-2638"},
        {"tier": "JCR Q2", "name": "Pediatric Physical Therapy", "issn": "0898-5669"}
    ],
    "cardio": [
        {"tier": "JCR Q1", "name": "Heart & Lung", "issn": "0147-9563"},
        {"tier": "JCR Q1", "name": "European Journal of Preventive Cardiology", "issn": "2047-4873"},
        {"tier": "JCR Q2", "name": "Journal of Cardiopulmonary Rehabilitation and Prevention", "issn": "1932-750X"}
    ],
    "dysphagia": [
        {"tier": "JCR Q1", "name": "Dysphagia", "issn": "0179-051X"},
        {"tier": "JCR Q1", "name": "Journal of Speech, Language, and Hearing Research", "issn": "1092-4388"},
        {"tier": "JCR Q1", "name": "American Journal of Speech-Language Pathology", "issn": "1058-0360"}
    ],
    "emg": [
        {"tier": "JCR Q1", "name": "Clinical Neurophysiology", "issn": "1388-2457"},
        {"tier": "JCR Q2", "name": "Muscle & Nerve", "issn": "0148-639X"},
        {"tier": "JCR Q2", "name": "Journal of Electromyography and Kinesiology", "issn": "1050-6411"}
    ],
    "msk": [
        {"tier": "JCR Q1", "name": "Ultrasound in Medicine and Biology", "issn": "0301-5629"},
        {"tier": "JCR Q2", "name": "Journal of Ultrasound in Medicine", "issn": "0278-4297"},
        {"tier": "JCR Q2", "name": "Skeletal Radiology", "issn": "0364-2348"}
    ],
    "pain": [
        {"tier": "JCR Q1", "name": "Pain", "issn": "0304-3959"},
        {"tier": "JCR Q1", "name": "Regional Anesthesia and Pain Medicine", "issn": "1098-7339"},
        {"tier": "JCR Q2", "name": "The Clinical Journal of Pain", "issn": "0749-8047"},
        {"tier": "JCR Q2", "name": "Pain Medicine", "issn": "1526-2375"}
    ],
    "sports": [
        {"tier": "JCR Q1", "name": "The American Journal of Sports Medicine", "issn": "0363-5465"},
        {"tier": "JCR Q1", "name": "British Journal of Sports Medicine", "issn": "0306-3674"},
        {"tier": "JCR Q1", "name": "Sports Medicine", "issn": "0112-1642"}
    ],
    "prosthetics": [
        {"tier": "JCR Q2", "name": "Prosthetics and Orthotics International", "issn": "0309-3646"},
        {"tier": "ESCI", "name": "Journal of Prosthetics and Orthotics", "issn": "1040-8800"}
    ]
}

TOP_MEDICAL_JOURNALS = [
    {"tier": "🥇 General Top", "name": "The New England Journal of Medicine (NEJM)", "issn": "0028-4793"},
    {"tier": "🥇 General Top", "name": "The Lancet", "issn": "0140-6736"},
    {"tier": "🥇 General Top", "name": "JAMA", "issn": "0098-7484"},
    {"tier": "🥇 General Top", "name": "The BMJ", "issn": "0959-8138"},
    {"tier": "🚀 Nature/Digital", "name": "Nature Medicine", "issn": "1078-8956"},
    {"tier": "🚀 Nature/Digital", "name": "The Lancet Digital Health", "issn": "2589-7500"},
    {"tier": "🚀 Nature/Digital", "name": "npj Digital Medicine", "issn": "2398-6352"},
    {"tier": "🧠 Neuro Top", "name": "The Lancet Neurology", "issn": "1474-4422"},
    {"tier": "💻 Health Info", "name": "Journal of Medical Internet Research (JMIR)", "issn": "1438-8871"},
    {"tier": "⚙️ IEEE Eng", "name": "IEEE Journal of Biomedical and Health Informatics", "issn": "2168-2194"},
    {"tier": "🤖 Medical AI", "name": "Artificial Intelligence in Medicine", "issn": "0933-3657"}
]

if BOT_NAME == "ai":
    all_rehab_journals = []
    for j_list in JOURNALS_DB.values():
        all_rehab_journals.extend(j_list)
    unique_rehab = {j['issn']: j for j in all_rehab_journals}.values()
    BOT_JOURNALS = TOP_MEDICAL_JOURNALS + list(unique_rehab)

    PERIODS = [
        {"label": f"[{BOT_KOR_NAME}] 최신 AI 융합 트렌드 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 80},
        {"label": f"[{BOT_KOR_NAME}] AI 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 100}
    ]
    AI_SEARCH_KEYWORDS = '"artificial intelligence"|"machine learning"|"deep learning"|"language model"|"chatgpt"|"computer vision"|"natural language processing"'
else:
    BOT_JOURNALS = JOURNALS_DB.get(BOT_NAME, [])
    PERIODS = [
        {"label": f"[{BOT_KOR_NAME}] 최신 트렌드 발굴 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 50},
        {"label": f"[{BOT_KOR_NAME}] 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 70},
        {"label": f"[{BOT_KOR_NAME}] 클래식 족보 (과거 8~15년)", "start": current_year - 14, "end": current_year - 7, "top_n": 60}
    ]
    AI_SEARCH_KEYWORDS = ""

TARGET_ISSNS = "|".join([j["issn"] for j in BOT_JOURNALS])
