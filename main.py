import os
import time
import schedule
from datetime import datetime

import config
from logger import log
from db_manager import DBManager
from openalex_client import get_top_citations, fetch_paper_meta
from zotero_client import ZoteroClient
from gemini_client import analyze_papers
from notifier import notify_all

def run_pipeline():
    log.info("=====================================================")
    log.info(f"🚀 AI 스마트 연구 기획봇 가동 시작: [{config.BOT_KOR_NAME}]")
    log.info("=====================================================")

    zot_client = ZoteroClient()
    db = DBManager()

    ai_analysis_payload = []
    new_found = False

    for period in config.PERIODS:
        label = period['label']
        target_n = period['top_n']
        log.info(f"[{label}] 상위 {target_n}편 초고속 수집 시작...")

        top_refs = get_top_citations(period['start'], period['end'], target_n)

        for rank, (ref_id, count) in enumerate(top_refs, 1):
            db_paper = db.get_paper(ref_id)

            if db_paper:
                paper_data = {
                    "title": db_paper['title'],
                    "year": db_paper['year'],
                    "count": count,
                    "abstract": db_paper['abstract'],
                    "doi": db_paper['doi'],
                    "rank": rank
                }
                ai_analysis_payload.append(paper_data)
                log.info(f" -> 🔄 DB 캐시에서 로드: [{rank}위] {db_paper['title'][:30]}...")
                continue

            meta = fetch_paper_meta(ref_id)
            if not meta:
                continue

            result = zot_client.save_paper(meta, count)
            if result:
                db.save_paper(ref_id, result['title'], result['year'], result['abstract'], result['doi'])
                result['rank'] = rank
                ai_analysis_payload.append(result)

                if result["status"] == "added":
                    new_found = True
                    log.info(f" -> ✅ Zotero 신규 저장: [{rank}위] {result['title'][:30]}...")
                else:
                    log.info(f" -> 🔄 Zotero 동기화: [{rank}위] {result['title'][:30]}...")

            time.sleep(1)

        log.info(f"[{label}] 목표 수량 수집 완료.\n")

    if ai_analysis_payload:
        log.info(f"🤖 총 {len(ai_analysis_payload)}편의 논문으로 Gemini 2.5 Flash 스마트 분석 시작... (최대 10분 대기)")
        ai_html_report = analyze_papers(ai_analysis_payload)

        raw_list_html = f"<h3>📚 전체 수집 논문 원본 리스트 (Zotero 폴더 ID: {config.ZOTERO_FOLDER_ID})</h3><ul>"
        for p in ai_analysis_payload:
            raw_list_html += f"<li style='margin-bottom: 8px;'><b>[{p.get('rank', 0)}위] {p['title']}</b> ({p['year']})<br>동시인용: {p['count']}회 | 논문 링크: <a href='{p['doi']}'>{p['doi']}</a></li>"
        raw_list_html += "</ul>"

        final_email_html = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: auto;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">🤖 [{config.BOT_KOR_NAME}] 이달의 연구 기획 브리핑</h1>
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #3498db; margin: 20px 0;">
                {ai_html_report}
            </div>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            {raw_list_html}
        </div>
        """

        current_month = datetime.now().month
        tg_msg = f"🧠 <b>[{config.BOT_KOR_NAME}] {current_month}월 연구 브리핑 완료!</b>\n\n총 {len(ai_analysis_payload)}편의 핵심 논문 수집 및 AI 기획안 작성이 완료되었습니다.\n\n이메일로 방금 발송되었습니다."

        notify_all(f"🚀 [AI Rehab Bot] {config.BOT_KOR_NAME} {current_month}월 연구 기획 브리핑 도착", tg_msg, final_email_html)
        log.info("✅ 신규 Zotero 저장 및 리포트 발송 완료.")
    else:
        log.info("이번 스캔에서 분석할 논문이 없습니다.")

    log.info("=====================================================\n")

def job_condition():
    db = DBManager()
    now = datetime.now()
    current_month_num = now.month
    current_year_month_str = now.strftime("%Y-%m")

    # 1. 이번 달이 내 담당 월(Month)인지 확인
    if current_month_num != config.RUN_MONTH:
        log.info(f"💤 이번 달({current_month_num}월)은 내 당번이 아닙니다. (내 담당: 매년 {config.RUN_MONTH}월)")
        return

    # 2. 내 담당 월이라면, 이번 달에 이미 브리핑을 보냈는지 확인 (중복 발송 방지 및 Catch-up 보장)
    last_run_month = db.get_setting("last_run_month")
    if last_run_month == current_year_month_str:
        log.info(f"✅ 이번 달({current_year_month_str}) 담당 브리핑은 이미 성공적으로 발송 완료되었습니다. 내년 {config.RUN_MONTH}월까지 1년간 휴식합니다.")
        return

    # 3. 내 당번 월이고 아직 안 보냈다면 실행! (06:30 정시이거나 NAS가 늦게 켜졌을 때 즉시 실행)
    log.info(f"🔥 드디어 내 차례입니다! 이번 달({current_year_month_str}) [{config.BOT_KOR_NAME}] 브리핑을 시작합니다!")
    try:
        run_pipeline()
        # 에러 없이 완료되었을 때만 DB에 이번 달 '완료 도장'을 남김
        db.set_setting("last_run_month", current_year_month_str)
        log.info(f"💾 {current_year_month_str} 브리핑 완료 기록을 DB에 안전하게 저장했습니다.")
    except Exception as e:
        log.error(f"❌ 파이프라인 실행 중 오류 발생 (다음 실행 주기 또는 내일 06:30에 재시도합니다): {e}")

if __name__ == "__main__":
    log.info(f"✨ 봇 세팅 완료: [{config.BOT_KOR_NAME}] 비서는 매년 '{config.RUN_MONTH}월'에 단 한 번 가동되며, 오전 06:30에 브리핑을 준비합니다.")

    # 1. 도커 컨테이너가 켜질 때 즉시 1회 체크 (NAS가 오랫동안 꺼져있어 스케줄을 놓쳤을 경우를 대비한 복구 로직)
    job_condition()

    # 2. 이후 매일 아침 06:30 정기 체크
    schedule.every().day.at("06:30").do(job_condition)

    while True:
        schedule.run_pending()
        time.sleep(60)
