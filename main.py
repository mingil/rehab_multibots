import os
import time
import schedule
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

import config
from logger import setup_logger
from db_manager import DBManager
from report_builder import build_reports

from openalex_client import get_top_citations, fetch_paper_meta
from zotero_client import ZoteroClient
from gemini_client import analyze_papers
from notifier import notify_all

def run_pipeline(bot_cfg):
    log = setup_logger(bot_cfg["bot_name"], bot_cfg["log_file"])

    log.info("=====================================================")
    log.info(f"🚀 AI 스마트 연구 기획봇 마스터 스케줄러 가동: [{bot_cfg['bot_kor_name']}]")
    log.info("=====================================================")

    zot_client = ZoteroClient(bot_cfg, log)
    db = DBManager(bot_cfg["db_file"], logger=log)
    ai_analysis_payload = []
    seen_refs = {}

    # 1. 🔍 데이터 수집 및 Zotero 저장 파이프라인
    log.info("🔍 [1단계] 기간별 논문 데이터 탐색 및 Zotero 동기화를 시작합니다.")

    total_periods = len(bot_cfg["periods"])
    for p_idx, period in enumerate(bot_cfg["periods"], 1):
        target_n = period['top_n']

        # 🔥 실시간 로그 1: 현재 어떤 기간(Period)을 탐색 중인지 출력
        log.info(f" ⏳ [{p_idx}/{total_periods}] OpenAlex 검색 중: {period['label']} (목표: Top {target_n}편)")

        top_refs = get_top_citations(bot_cfg, period['start'], period['end'], target_n, log)
        total_targets = len(top_refs)

        if total_targets > 0:
            log.info(f" 💾 총 {total_targets}편의 인용 족보를 확보했습니다. DB 검증 및 메타 파싱을 진행합니다...")
        else:
            log.warning(f" ⚠️ [결과 없음] 해당 기간의 논문을 찾지 못했습니다.")
            continue

        for idx, (ref_id, count) in enumerate(top_refs, 1):

            # 🔥 실시간 로그 2: 20건마다 진행 상황(Progress) 알림 (터미널 멈춤 방지)
            if idx == 1 or idx % 20 == 0 or idx == total_targets:
                log.info(f"   ... 논문 처리 진행률: {idx}/{total_targets} 편 완료")

            # 🛡️ 기간 간 중복 논문 통합 (동일 논문이 여러 기간에 인용된 경우 피인용 횟수 합산 후 중복 제외)
            if ref_id in seen_refs:
                seen_refs[ref_id]["count"] += count
                continue

            db_paper = db.get_paper(ref_id)
            if db_paper and db_paper.get('journal') and db_paper.get('journal') != "Unknown Journal":
                paper_data = {
                    "title": db_paper['title'], "year": db_paper['year'], "count": count,
                    "abstract": db_paper['abstract'], "doi": db_paper['doi'],
                    "journal": db_paper['journal'], "authors": db_paper['authors'],
                    "study_design": db_paper.get('study_design', 'Original Research')
                }
                seen_refs[ref_id] = paper_data
                ai_analysis_payload.append(paper_data)
                continue

            meta = fetch_paper_meta(ref_id, log)
            if not meta: continue

            journal = meta.get('_journal', 'Unknown Journal')
            authors_str = meta.get('_authors', 'Unknown Authors')
            study_design = meta.get('_study_design', 'Original Research')

            result = zot_client.save_paper(meta, count)
            if result:
                db.save_paper(ref_id, result['title'], result['year'], result['abstract'], result['doi'], journal, authors_str, study_design)
                result.update({"journal": journal, "authors": authors_str, "study_design": study_design})
                seen_refs[ref_id] = result
                ai_analysis_payload.append(result)

            # Zotero API 보호를 위한 필수 휴식 시간
            time.sleep(1)

    # 2. 🧠 AI 분석 및 리포트 발송 파이프라인
    if ai_analysis_payload:
        log.info(f" 📊 전체 기간 수집 완료 (총 {len(ai_analysis_payload)}편). 피인용 횟수 기준 랭킹을 정렬합니다.")

        # 전체 논문을 피인용 횟수(count) 기준으로 완벽하게 내림차순 정렬
        ai_analysis_payload.sort(key=lambda x: x.get('count', 0), reverse=True)

        # 정렬된 순서대로 1위부터 끝까지 순위(rank)를 새롭게 다시 매겨줍니다.
        for new_rank, paper in enumerate(ai_analysis_payload, 1):
            paper['rank'] = new_rank

        ai_md_report = analyze_papers(ai_analysis_payload, log)

        log.info(" 🎨 마크다운 및 HTML 리포트 디자인 렌더링 중...")
        reports = build_reports(bot_cfg, ai_md_report, ai_analysis_payload)

        # 3. 💾 로컬 백업
        try:
            local_md_path = os.path.join(config.REPORTS_DIR, reports["md_filename"])
            local_html_path = os.path.join(config.REPORTS_DIR, reports["html_filename"])

            with open(local_md_path, "w", encoding="utf-8") as f:
                f.write(reports["md_content"])
            with open(local_html_path, "w", encoding="utf-8") as f:
                f.write(reports["html_content"])
            log.info(f" 💾 도커(NAS) 로컬 백업 완료: {reports['md_filename']}")
        except Exception as e:
            log.error(f" ❌ 로컬 파일 백업 중 오류 발생: {e}")

        # 4. 📨 외부 발송
        log.info(" 📨 이메일 및 텔레그램 발송을 시작합니다...")
        notify_all(
            subject=f"🚀 [AI 테마분류 심층 브리핑] {bot_cfg['bot_kor_name']} 도착",
            tg_msg=reports["tg_msg"],
            html_body=reports["html_content"],
            log=log,
            md_filename=reports["md_filename"],
            md_content=reports["md_content"]
        )
        log.info(f"✅ 리포트 발송 완료 및 스케줄러 사이클 종료")
    else:
        log.info("이번 스캔에서 분석할 논문이 없습니다.")


def job_master_scheduler():
    """매일 구동되며 현재 '월(Month)'에 맞는 봇을 찾아 실행합니다."""
    now = datetime.now()
    current_month = now.month
    current_year_month_str = now.strftime("%Y-%m")

    bot_cfg = config.get_bot_config(current_month)
    if not bot_cfg:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 이번 달({current_month}월) 예약된 스케줄이 없습니다.")
        return

    db = DBManager(bot_cfg["db_file"])
    if db.get_setting("last_run_month") == current_year_month_str:
        return

    try:
        run_pipeline(bot_cfg)
        db.set_setting("last_run_month", current_year_month_str)
    except Exception as e:
        print(f"실행 오류: {e}")


if __name__ == "__main__":
    print("=====================================================")
    print("👑 Rehab Multi-Bots: 단일 마스터 스케줄러 가동 준비 완료")
    print("=====================================================")

    job_master_scheduler()
    schedule.every().day.at("06:30").do(job_master_scheduler)

    while True:
        schedule.run_pending()
        time.sleep(60)
