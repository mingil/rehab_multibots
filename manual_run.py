import os
import sys
import time
import subprocess
from dotenv import load_dotenv

# 🌟 핵심 해결책: 현재 스크립트가 위치한 폴더의 '절대 경로'를 추출하여 고정합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# .env 파일도 절대 경로를 명시하여 확실하게 불러옵니다.
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 12개 봇의 도커 환경변수 설정값 복제본
BOTS = [
    {"BOT_NAME": "general", "BOT_KOR_NAME": "일반 및 포괄 재활", "ZOTERO_FOLDER_ID": "NP96UXQT", "TARGET_ISSNS": "0003-9993|2234-0645|0894-9115|0269-2155|1934-1482|1650-1977|1973-9087|0963-8288"},
    {"BOT_NAME": "neuro", "BOT_KOR_NAME": "뇌신경 및 뇌졸중 재활", "ZOTERO_FOLDER_ID": "A6HACQEL", "TARGET_ISSNS": "0039-2499|1545-9683|1074-9357|1743-0003"},
    {"BOT_NAME": "sci", "BOT_KOR_NAME": "척수손상 재활", "ZOTERO_FOLDER_ID": "UX45UG5I", "TARGET_ISSNS": "1362-4393|1079-0268|2058-6124"},
    {"BOT_NAME": "peds", "BOT_KOR_NAME": "소아재활", "ZOTERO_FOLDER_ID": "TTDCGMN2", "TARGET_ISSNS": "0012-1622|0898-5669|0194-2638"},
    {"BOT_NAME": "cardio", "BOT_KOR_NAME": "심폐재활", "ZOTERO_FOLDER_ID": "I7H8G98B", "TARGET_ISSNS": "1932-750X|0147-9563|2047-4873"},
    {"BOT_NAME": "dysphagia", "BOT_KOR_NAME": "연하장애", "ZOTERO_FOLDER_ID": "4EJ6YKPI", "TARGET_ISSNS": "0179-051X|1092-4388|1058-0360"},
    {"BOT_NAME": "emg", "BOT_KOR_NAME": "근전도 및 전기진단", "ZOTERO_FOLDER_ID": "SKV3RN7G", "TARGET_ISSNS": "0148-639X|1388-2457|1050-6411"},
    {"BOT_NAME": "msk", "BOT_KOR_NAME": "근골격 및 초음파", "ZOTERO_FOLDER_ID": "QX28AV9Z", "TARGET_ISSNS": "0301-5629|0278-4297|0364-2348"},
    {"BOT_NAME": "pain", "BOT_KOR_NAME": "통증재활", "ZOTERO_FOLDER_ID": "XSC4ZQAX", "TARGET_ISSNS": "0304-3959|0749-8047|1526-2375|1098-7339"},
    {"BOT_NAME": "sports", "BOT_KOR_NAME": "스포츠재활", "ZOTERO_FOLDER_ID": "J52JPFK2", "TARGET_ISSNS": "0363-5465|0306-3674|0112-1642"},
    {"BOT_NAME": "prosthetics", "BOT_KOR_NAME": "의지보조기 및 생체역학", "ZOTERO_FOLDER_ID": "CKRLZRZ8", "TARGET_ISSNS": "0309-3646|1040-8800"},
    {"BOT_NAME": "ai", "BOT_KOR_NAME": "재활의학 인공지능(AI/ML) 융합", "ZOTERO_FOLDER_ID": "EYHM7ISA", "TARGET_ISSNS": "0003-9993|2234-0645|0894-9115|0269-2155|1934-1482|1650-1977|1973-9087|0963-8288|0039-2499|1545-9683|1074-9357|1743-0003|1362-4393|1079-0268|2058-6124|0012-1622|0898-5669|0194-2638|1932-750X|0147-9563|2047-4873|0179-051X|1092-4388|1058-0360|0148-639X|1388-2457|1050-6411|0301-5629|0278-4297|0364-2348|0304-3959|0749-8047|1526-2375|1098-7339|0363-5465|0306-3674|0112-1642|0309-3646|1040-8800"}
]

def run_bot(bot_config):
    print(f"\n====================================================")
    print(f"🚀 [{bot_config['BOT_KOR_NAME']}] 수동 파이프라인 가동 시작...")
    print(f"====================================================")

    custom_env = os.environ.copy()
    for key, value in bot_config.items():
        custom_env[key] = value

    # 🚀 파이썬 실행 코드를 한 줄로 만들되, 모듈 검색 경로(sys.path) 1순위에 강제로 현재 폴더(BASE_DIR)를 꽂아 넣습니다!
    exec_cmd = f"import sys; sys.path.insert(0, '{BASE_DIR}'); from main import run_pipeline; run_pipeline()"

    try:
        # sys.executable은 선생님께서 입력하신 아나콘다 파이썬을 자동으로 이어받습니다.
        # cwd=BASE_DIR 을 통해 프로세스의 작업 폴더도 강제 고정합니다.
        subprocess.run(
            [sys.executable, "-c", exec_cmd],
            env=custom_env,
            cwd=BASE_DIR,
            check=True
        )
        print(f"\n✅ [{bot_config['BOT_KOR_NAME']}] 브리핑 발송이 성공적으로 완료되었습니다!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 파이프라인 실행 중 에러가 발생했습니다: {e}")

def main():
    while True:
        print("\n🤖 Rehab Multi-Bots 만능 수동 실행 리모컨 🤖")
        print(" (원하시는 봇의 번호를 선택해 주세요. 정규 스케줄에는 영향을 주지 않습니다.)\n")

        for i, bot in enumerate(BOTS, 1):
            print(f" {i:2d}. {bot['BOT_KOR_NAME']}")

        print("-" * 55)
        print(" 99. 🌟 전체 12개 분과 연속 가동 (API 차단 방지용 1분 쿨타임 자동 적용)")
        print("  0. 종료하기")

        choice = input("\n👉 실행할 메뉴 번호를 입력하세요: ").strip()

        if choice == '0':
            print("👋 수동 실행을 종료합니다.")
            break

        elif choice == '99':
            print("\n🔥 전체 12개 분과 연속 가동을 시작합니다. (API 과부하 방지를 위해 1분씩 대기합니다.)")
            for i, bot in enumerate(BOTS):
                run_bot(bot)
                if i < len(BOTS) - 1:
                    print("\n⏳ API 차단 방어막 작동: 60초간 대기 후 다음 봇으로 넘어갑니다...\n")
                    time.sleep(60)
            print("\n🎉 12개 분과 전체 수동 실행이 완벽하게 끝났습니다! 이메일과 텔레그램을 확인해 보세요.")
            break

        elif choice.isdigit() and 1 <= int(choice) <= 12:
            idx = int(choice) - 1
            run_bot(BOTS[idx])

        else:
            print("⚠️ 잘못된 번호입니다. 0~12, 또는 99를 입력해 주세요.")

if __name__ == "__main__":
    main()
