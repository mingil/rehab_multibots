import os
import time
import schedule
from datetime import datetime
import markdown # 🚀 순수 마크다운을 예쁜 HTML 메일로 자동 변환해 주는 라이브러리 추가

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
                    log.info(f" -> ✅ Zotero 신규 저장: [{rank}위] {result['title'][:30]}...")
                else:
                    log.info(f" -> 🔄 Zotero 동기화: [{rank}위] {result['title'][:30]}...")

            time.sleep(1)

        log.info(f"[{label}] 목표 수량 수집 완료.\n")

    if ai_analysis_payload:
        log.info(f"🤖 총 {len(ai_analysis_payload)}편의 논문으로 Gemini 2.5 Flash 스마트 분석 시작... (최대 10분 대기)")

        # 1. AI에게서 '순수 마크다운' 포맷의 글을 받아옵니다.
        ai_md_report = analyze_papers(ai_analysis_payload)

        current_date = datetime.now().strftime("%Y-%m-%d")

        # 🚀 2. 옵시디언 전용 YAML Frontmatter (메타데이터 꼬리표) 작성
        frontmatter = f"""---
title: "[{config.BOT_KOR_NAME}] AI 연구 기획 브리핑"
date: {current_date}
category: "{config.BOT_KOR_NAME}"
tags: [rehab_bot, AI_Briefing, {config.BOT_NAME}]
---

# 🤖 [{config.BOT_KOR_NAME}] 스마트 연구 기획 브리핑

"""
        # 🚀 3. Zotero 원본 논문 리스트를 옵시디언 "투두 체크리스트(- [ ])" 형태로 작성
        raw_list_md = f"\n\n---\n\n## 📚 전체 수집 논문 체크리스트\n*Zotero 폴더 ID: {config.ZOTERO_FOLDER_ID}*\n\n"
        for p in ai_analysis_payload:
            raw_list_md += f"- [ ] **[{p.get('rank', 0)}위] {p['title']}** ({p['year']}) | 피인용: {p['count']}회 | [DOI 링크]({p['doi']})\n"

        # 🚀 4. 첨부할 최종 옵시디언 파일(.md) 텍스트 및 파일명 조립!
        final_md_content = frontmatter + ai_md_report + raw_list_md
        md_filename = f"Rehab_Briefing_{config.BOT_NAME}_{current_date}.md"

        # 🚀 5. 이메일 본문용: 순수 마크다운을 예쁜 HTML로 자동 변환!
        # (extensions 옵션으로 체크리스트와 줄바꿈을 이메일에서도 그대로 예쁘게 유지합니다)
        html_content = markdown.markdown(ai_md_report + raw_list_md, extensions=['extra', 'nl2br'])

        final_email_html = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: auto;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">🤖 [{config.BOT_KOR_NAME}] 이달의 연구 기획 브리핑</h1>
            <p style="color: #e74c3c; font-weight: bold;">💎 옵시디언(Obsidian) 보관용 완벽한 .md 파일이 메일에 첨부되어 있습니다! 다운로드하여 옵시디언에 드래그하세요.</p>
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #3498db; margin: 20px 0;">
                {html_content}
            </div>
        </div>
        """

        current_month = datetime.now().month
        tg_msg = f"🧠 <b>[{config.BOT_KOR_NAME}] {current_month}월 연구 브리핑 완료!</b>\n\n총 {len(ai_analysis_payload)}편의 핵심 논문 수집 및 AI 기획안 작성이 완료되었습니다.\n\n이메일(옵시디언용 .md 첨부파일 포함)로 방금 발송되었습니다."

        # 옵시디언 첨부파일 데이터를 실어서 알림 전송!
        notify_all(f"🚀 [AI Rehab Bot] {config.BOT_KOR_NAME} {current_month}월 브리핑 도착", tg_msg, final_email_html, md_filename=md_filename, md_content=final_md_content)
        log.info(f"✅ 신규 Zotero 저장 및 리포트 발송 완료 (옵시디언 첨부파일: {md_filename})")
    else:
        log.info("이번 스캔에서 분석할 논문이 없습니다.")

    log.info("=====================================================\n")

def job_condition():
    db = DBManager()
    now = datetime.now()
    current_month_num = now.month
    current_year_month_str = now.strftime("%Y-%m")

    if current_month_num != config.RUN_MONTH:
        log.info(f"💤 이번 달({current_month_num}월)은 내 당번이 아닙니다. (내 담당: 매년 {config.RUN_MONTH}월)")
        return

    last_run_month = db.get_setting("last_run_month")
    if last_run_month == current_year_month_str:
        log.info(f"✅ 이번 달({current_year_month_str}) 담당 브리핑은 이미 성공적으로 발송 완료되었습니다. 내년 {config.RUN_MONTH}월까지 1년간 휴식합니다.")
        return

    log.info(f"🔥 드디어 내 차례입니다! 이번 달({current_year_month_str}) [{config.BOT_KOR_NAME}] 브리핑을 시작합니다!")
    try:
        run_pipeline()
        db.set_setting("last_run_month", current_year_month_str)
        log.info(f"💾 {current_year_month_str} 브리핑 완료 기록을 DB에 안전하게 저장했습니다.")
    except Exception as e:
        log.error(f"❌ 파이프라인 실행 중 오류 발생 (다음 실행 주기 또는 내일 06:30에 재시도합니다): {e}")

if __name__ == "__main__":
    log.info(f"✨ 봇 세팅 완료: [{config.BOT_KOR_NAME}] 비서는 매년 '{config.RUN_MONTH}월'에 단 한 번 가동되며, 오전 06:30에 브리핑을 준비합니다.")

    job_condition()
    schedule.every().day.at("06:30").do(job_condition)

    while True:
        schedule.run_pending()
        time.sleep(60)
