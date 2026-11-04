import os
import sys
import time
import subprocess
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 동적 설정을 가져오기 위해 config 임포트
sys.path.insert(0, BASE_DIR)
import config

def run_bot(month_idx):
    bot_cfg = config.get_bot_config(month_idx)
    if not bot_cfg:
        print(f"❌ {month_idx}월에 해당하는 봇 설정이 없습니다.")
        return

    print(f"\n====================================================")
    print(f"🚀 [{bot_cfg['bot_kor_name']}] 수동 파이프라인 가동 시작...")
    print(f"====================================================")

    # 파이프라인 꼬임을 방지하기 위해 단일 실행용 서브프로세스 셸 명령어 생성
    exec_cmd = f"""
import sys
sys.path.insert(0, '{BASE_DIR}')
import config
from main import run_pipeline
cfg = config.get_bot_config({month_idx})
run_pipeline(cfg)
"""
    try:
        subprocess.run(
            [sys.executable, "-c", exec_cmd],
            cwd=BASE_DIR,
            check=True
        )
        print(f"\n✅ [{bot_cfg['bot_kor_name']}] 브리핑 발송 및 백업이 성공적으로 완료되었습니다!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 파이프라인 실행 중 에러가 발생했습니다: {e}")

def main():
    while True:
        print("\n🤖 Rehab Multi-Bots 만능 수동 실행 리모컨 🤖")
        print(" (원하시는 봇의 번호(월)를 선택해 주세요. 정규 스케줄에는 영향을 주지 않습니다.)\n")

        # config.BOT_REGISTRY에서 동적으로 분과 목록을 불러와 출력합니다.
        for month in sorted(config.BOT_REGISTRY.keys()):
            info = config.BOT_REGISTRY[month]
            print(f" {month:2d}월: {info['kor_name']}")

        print("-" * 55)
        print(" 99. 🌟 전체 12개 분과 연속 가동 (API 차단 방지용 1분 쿨타임 자동 적용)")
        print("  0. 종료하기")

        choice = input("\n👉 실행할 메뉴(월) 번호를 입력하세요: ").strip()

        if choice == '0':
            print("👋 수동 실행을 종료합니다.")
            break

        elif choice == '99':
            print("\n🔥 전체 12개 분과 연속 가동을 시작합니다. (API 과부하 방지를 위해 1분씩 대기합니다.)")
            months = sorted(list(config.BOT_REGISTRY.keys()))
            for idx, m in enumerate(months):
                run_bot(m)
                if idx < len(months) - 1:
                    print("\n⏳ API 차단 방어막 작동: 60초간 대기 후 다음 분과로 넘어갑니다...\n")
                    time.sleep(60)
            print("\n🎉 12개 분과 전체 수동 실행이 완벽하게 끝났습니다! 이메일과 로컬 백업 폴더를 확인해 보세요.")
            break

        elif choice.isdigit() and int(choice) in config.BOT_REGISTRY:
            run_bot(int(choice))

        else:
            print("⚠️ 잘못된 번호입니다. 1~12, 99, 0 중에서 정확하게 입력해 주세요.")

if __name__ == "__main__":
    main()
