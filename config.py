import os
from datetime import datetime
from dotenv import load_dotenv

# ==============================================================
# 📂 1. [완벽 폴더 구조 정리] 데이터, 로그, 리포트를 전용 폴더로 격리
# ==============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports") # 💡 월별 백업 파일 저장용 신규 폴더

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, ".env"))

# ==============================================================
# 🔐 2. 환경 변수 (API 키 및 인증 정보)
# ==============================================================
USER_EMAIL = os.getenv("USER_EMAIL")
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL") or USER_EMAIL
OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY") 
ZOTERO_USER_ID = os.getenv("ZOTERO_USER_ID")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# ==============================================================
# 🎯 3. 분과별 공식 탐색 대상 저널 DB (Target Journal Pool)
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

# AI 트랙(12월)을 위한 '전체 저널 목록' 사전 병합 로직
all_rehab_journals = []
for j_list in JOURNALS_DB.values():
    all_rehab_journals.extend(j_list)
unique_rehab = list({j['issn']: j for j in all_rehab_journals}.values())
JOURNALS_DB["ai"] = TOP_MEDICAL_JOURNALS + unique_rehab

# ==============================================================
# 🤖 4. [단일 진실 공급원] 12개 분과 봇 중앙 통합 마스터 설정
# ==============================================================
# key 값이 실행 월(1~12월)을 의미합니다.
BOT_REGISTRY = {
    1: {"id": "general", "kor_name": "일반 및 포괄 재활", "zotero_id": "NP96UXQT"},
    2: {"id": "neuro", "kor_name": "뇌신경 및 뇌졸중 재활", "zotero_id": "A6HACQEL"},
    3: {"id": "sci", "kor_name": "척수손상 재활", "zotero_id": "UX45UG5I"},
    4: {"id": "peds", "kor_name": "소아재활", "zotero_id": "TTDCGMN2"},
    5: {"id": "cardio", "kor_name": "심폐재활", "zotero_id": "I7H8G98B"},
    6: {"id": "dysphagia", "kor_name": "연하장애", "zotero_id": "4EJ6YKPI"},
    7: {"id": "emg", "kor_name": "근전도 및 전기진단", "zotero_id": "SKV3RN7G"},
    8: {"id": "msk", "kor_name": "근골격 및 초음파", "zotero_id": "QX28AV9Z"},
    9: {"id": "pain", "kor_name": "통증재활", "zotero_id": "XSC4ZQAX"},
    10: {"id": "sports", "kor_name": "스포츠재활", "zotero_id": "J52JPFK2"},
    11: {"id": "prosthetics", "kor_name": "의지보조기 및 생체역학", "zotero_id": "CKRLZRZ8"},
    12: {"id": "ai", "kor_name": "재활의학 인공지능(AI/ML) 융합", "zotero_id": "EYHM7ISA"}
}

# ==============================================================
# ⚙️ 5. [동적 설정 생성기] 스케줄러가 매달 호출할 팩토리 함수
# ==============================================================
def get_bot_config(month: int):
    """지정된 월(Month)에 맞는 봇의 모든 설정을 딕셔너리로 동적 반환합니다."""
    if month not in BOT_REGISTRY:
        return None

    info = BOT_REGISTRY[month]
    bot_id = info["id"]
    kor_name = info["kor_name"]
    current_year = datetime.now().year

    journals = JOURNALS_DB.get(bot_id, [])

    config_data = {
        "run_month": month,
        "bot_name": bot_id,
        "bot_kor_name": kor_name,
        "zotero_folder_id": info["zotero_id"],
        "bot_journals": journals,
        "target_issns": "|".join([j["issn"] for j in journals]),
        "db_file": os.path.join(DATA_DIR, f"history_{bot_id}.db"),
        "log_file": os.path.join(LOGS_DIR, f"app_{bot_id}.log"),
    }

    if bot_id == "ai":
        config_data["ai_search_keywords"] = '"artificial intelligence"|"machine learning"|"deep learning"|"language model"|"chatgpt"|"computer vision"|"natural language processing"'
        config_data["periods"] = [
            {"label": f"[{kor_name}] 최신 AI 융합 트렌드 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 80},
            {"label": f"[{kor_name}] AI 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 100}
        ]
    else:
        config_data["ai_search_keywords"] = ""
        config_data["periods"] = [
            {"label": f"[{kor_name}] 최신 트렌드 발굴 (최근 1~3년)", "start": current_year - 2, "end": current_year, "top_n": 50},
            {"label": f"[{kor_name}] 메인스트림 주류 (과거 4~7년)", "start": current_year - 6, "end": current_year - 3, "top_n": 70},
            {"label": f"[{kor_name}] 클래식 족보 (과거 8~15년)", "start": current_year - 14, "end": current_year - 7, "top_n": 60}
        ]

    return config_data
