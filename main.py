import os
import re
import time
import schedule
import warnings
from datetime import datetime
import markdown

warnings.filterwarnings("ignore")

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

        top_refs = get_top_citations(period['start'], period['end'], target_n)
        for rank, (ref_id, count) in enumerate(top_refs, 1):
            db_paper = db.get_paper(ref_id)
            if db_paper and db_paper.get('journal') and db_paper.get('journal') != "Unknown Journal":
                paper_data = {
                    "title": db_paper['title'], "year": db_paper['year'], "count": count,
                    "abstract": db_paper['abstract'], "doi": db_paper['doi'],
                    "journal": db_paper['journal'], "authors": db_paper['authors'],
                    "study_design": db_paper.get('study_design', 'Original Research'), "rank": rank
                }
                ai_analysis_payload.append(paper_data)
                continue

            meta = fetch_paper_meta(ref_id)
            if not meta: continue

            journal = meta.get('_journal', 'Unknown Journal')
            authors_str = meta.get('_authors', 'Unknown Authors')
            study_design = meta.get('_study_design', 'Original Research')

            result = zot_client.save_paper(meta, count)
            if result:
                db.save_paper(ref_id, result['title'], result['year'], result['abstract'], result['doi'], journal, authors_str, study_design)
                result.update({"rank": rank, "journal": journal, "authors": authors_str, "study_design": study_design})
                ai_analysis_payload.append(result)
            time.sleep(1)

    if ai_analysis_payload:
        ai_md_report = analyze_papers(ai_analysis_payload)
        current_date = datetime.now().strftime("%Y-%m-%d")
        total_papers = len(ai_analysis_payload)

        md_journal_table = "\n### 🎯 공식 탐색 대상 저널 (Target Journal Pool)\n\n"
        md_journal_table += "| 등급 (Tier) | 저널명 (Journal) | ISSN |\n"
        md_journal_table += "| :---: | :--- | :---: |\n"

        html_journal_table = """
        <div style="margin: 30px 0;">
            <h2 style="font-size: 19px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; font-weight: 800;">🎯 공식 탐색 대상 저널 (Target Journal Pool)</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14.5px; border-radius: 8px; overflow: hidden; box-shadow: 0 0 0 1px #e2e8f0;">
                <thead>
                    <tr>
                        <th style="padding: 12px 15px; border-bottom: 2px solid #cbd5e1; background-color: #f1f5f9; text-align: center; color: #1e293b; width: 20%;">등급 (Tier)</th>
                        <th style="padding: 12px 15px; border-bottom: 2px solid #cbd5e1; background-color: #f1f5f9; text-align: left; color: #1e293b; width: 60%;">저널명 (Journal)</th>
                        <th style="padding: 12px 15px; border-bottom: 2px solid #cbd5e1; background-color: #f1f5f9; text-align: center; color: #1e293b; width: 20%;">ISSN</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, j in enumerate(config.BOT_JOURNALS):
            md_journal_table += f"| {j['tier']} | **{j['name']}** | `{j['issn']}` |\n"
            bg_color = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            html_journal_table += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 10px 15px; border-bottom: 1px solid #e2e8f0; text-align: center; font-weight: 600; color: #475569;">{j['tier']}</td>
                    <td style="padding: 10px 15px; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: #1e40af;">{j['name']}</td>
                    <td style="padding: 10px 15px; border-bottom: 1px solid #e2e8f0; text-align: center; color: #64748b;"><code>{j['issn']}</code></td>
                </tr>
            """
        html_journal_table += "</tbody></table></div>"

        # 📑 [TRACK 1] 옵시디언 전용 Markdown 완벽 조립
        frontmatter = f"""---
title: "[{config.BOT_KOR_NAME}] AI 1:1 심층 연구 기획 브리핑"
date: {current_date}
category: "{config.BOT_KOR_NAME}"
zotero_folder_name: "{config.BOT_KOR_NAME}"
zotero_folder_id: "{config.ZOTERO_FOLDER_ID}"
total_papers_analyzed: {total_papers}
tags: [rehab_bot, AI_Briefing, {config.BOT_NAME}, Deep_Dive]
---
# 🤖 [{config.BOT_KOR_NAME}] 스마트 연구 기획 브리핑

> **🗂️ 메타데이터 대시보드**
> - **대상 분과:** {config.BOT_KOR_NAME}
> - **Zotero 폴더명:** {config.BOT_KOR_NAME} (ID: `{config.ZOTERO_FOLDER_ID}`)
> - **총 수집 논문:** {total_papers}편

{md_journal_table}
"""
        raw_list_md = f"\n\n---\n\n## 📚 원본 논문 체크리스트 (총 {total_papers}편)\n\n"
        for p in ai_analysis_payload:
            raw_list_md += f"- [ ] **[{p.get('rank', 0)}위] [{p['title']}]({p['doi']})** ({p['year']})\n"
            raw_list_md += f"    - 👨‍🔬 **저자:** {p['authors']} | 📓 **저널:** *{p['journal']}*\n"
            raw_list_md += f"    - 🧬 **연구 설계:** {p['study_design']} | 📈 **피인용:** {p['count']}회\n"
            raw_list_md += f"    - 🔗 **DOI:** `{p['doi']}`\n\n"

        final_md_content = frontmatter + ai_md_report + raw_list_md
        md_filename = f"Rehab_Briefing_{config.BOT_NAME}_{current_date}.md"

        # 📑 [TRACK 2] 프리미엄 이메일 HTML
        ai_html_report = markdown.markdown(ai_md_report, extensions=['extra', 'nl2br'])

        dashboard_html = f"""
        <div class="dashboard">
            <div class="dash-item"><span class="dash-label">대상 분과</span><span class="dash-value">{config.BOT_KOR_NAME}</span></div>
            <div class="dash-item"><span class="dash-label">Zotero 폴더명</span><span class="dash-value">{config.BOT_KOR_NAME}</span></div>
            <div class="dash-item"><span class="dash-label">1:1 심층 분석 완료</span><span class="dash-value highlight">{total_papers}편 전체</span></div>
        </div>
        """

        raw_list_html = f"<h2 class='paper-list-header'>📚 원본 메타데이터 다이렉트 링크 (총 {total_papers}편)</h2>"
        for p in ai_analysis_payload:
            raw_list_html += f"""
            <div class="paper-card">
                <div class="paper-title">
                    <span style="color: #2563eb; margin-right: 4px;">[{p.get('rank', 0)}위]</span> <a href="{p['doi']}" target="_blank" style="color: #111111; text-decoration: none;">{p['title']}</a> <span style="color: #64748b; font-weight: 500;">({p['year']})</span>
                </div>
                <div class="paper-meta">
                    <span class="badge badge-author">👨‍🔬 {p['authors']}</span>
                    <span class="badge badge-journal">📓 {p['journal']}</span>
                    <span class="badge badge-design">🧬 {p['study_design']}</span>
                    <span class="badge badge-cite">📈 피인용 {p['count']}회</span>
                </div>
                <div class="paper-link">
                    🔗 <b>DOI:</b> <a href="{p['doi']}" target="_blank">{p['doi']}</a>
                </div>
            </div>
            """

        final_email_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ background-color: #f8fafc; margin: 0; padding: 40px 15px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; color: #1e293b; line-height: 1.7; -webkit-font-smoothing: antialiased; }}
            .container {{ max-width: 850px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background-color: #0f172a; padding: 35px 40px; color: #ffffff; border-bottom: 4px solid #3b82f6; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }}
            .body-wrap {{ padding: 40px; }}
            .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 30px; }}
            .dash-item {{ display: flex; flex-direction: column; }}
            .dash-label {{ font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }}
            .dash-value {{ font-size: 15px; color: #0f172a; font-weight: 600; }}
            .dash-value.highlight {{ color: #2563eb; font-weight: 800; }}
            .notice {{ background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px 20px; font-size: 14px; color: #1e40af; margin-bottom: 30px; font-weight: 600; line-height: 1.5; }}

            .content h1 {{ display: none; }}
            .content h2 {{ font-size: 20px; color: #0f172a; margin-top: 40px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; font-weight: 800; }}
            .content h3 {{ font-size: 18px; color: #1e293b; margin-top: 30px; margin-bottom: 12px; font-weight: 700; }}
            .content p {{ margin-bottom: 18px; font-size: 16px; word-break: keep-all; }}
            .content ul, .content ol {{ margin-bottom: 25px; padding-left: 24px; }}
            .content li {{ margin-bottom: 12px; font-size: 16px; }}

            /* 🚀 본문 다이렉트 링크 (진짜 논문 제목 클릭 렌더링) */
            .content a {{ color: #2563eb; text-decoration: underline; text-underline-offset: 3px; font-weight: 700; transition: all 0.2s; }}
            .content a:hover {{ background-color: #eff6ff; color: #1d4ed8; }}
            .content strong, .content b {{ color: #0f172a; font-weight: 700; background-color: #f1f5f9; padding: 2px 5px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}

            /* 하단 카드뷰 스타일 */
            .paper-list-header {{ font-size: 20px; color: #0f172a; margin-top: 50px; margin-bottom: 20px; font-weight: 800; border-bottom: 2px solid #111111; padding-bottom: 10px; }}
            .paper-card {{ background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-bottom: 16px; transition: box-shadow 0.2s, border-color 0.2s; }}
            .paper-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #94a3b8; }}
            .paper-title {{ font-size: 17px; font-weight: 700; color: #0f172a; margin-bottom: 12px; line-height: 1.4; }}
            .paper-title a:hover {{ color: #2563eb !important; text-decoration: underline !important; }}
            .paper-meta {{ margin-bottom: 14px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}

            .badge {{ font-size: 13.5px; padding: 4px 10px; border-radius: 6px; font-weight: 600; border: 1px solid transparent; }}
            .badge-author {{ background-color: #f8fafc; color: #475569; border-color: #e2e8f0; }}
            .badge-journal {{ background-color: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }}
            .badge-design {{ background-color: #f0fdf4; color: #15803d; border-color: #bbf7d0; }}
            .badge-cite {{ background-color: #fef2f2; color: #b91c1c; border-color: #fecaca; }}

            .paper-link {{ font-size: 14px; background-color: #f8fafc; padding: 12px 15px; border-radius: 6px; border: 1px solid #e2e8f0; }}
            .paper-link a {{ color: #2563eb; text-decoration: none; word-break: break-all; font-family: ui-monospace, Consolas, monospace; font-size: 13.5px; }}
            .paper-link a:hover {{ text-decoration: underline; }}

            .footer {{ background-color: #f8fafc; padding: 25px; text-align: center; font-size: 13px; color: #64748b; border-top: 1px solid #e2e8f0; }}
            @media only screen and (max-width: 600px) {{
                .body-wrap {{ padding: 20px; }}
                .dashboard {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 [{config.BOT_KOR_NAME}] 1:1 심층 연구 기획 브리핑</h1>
                </div>
                <div class="body-wrap">
                    <div class="notice">
                        📥 <b>옵시디언(Obsidian) 전용 백업 파일(.md) 첨부 안내</b><br>
                        이메일 하단 첨부파일을 옵시디언 <code>Inbox</code>에 넣으시면 1:1 인용 가이드가 영구 보존됩니다.
                    </div>
                    {dashboard_html}

                    {html_journal_table}

                    <div class="content">
                        {ai_html_report}
                    </div>
                    {raw_list_html}
                </div>
                <div class="footer">
                    본 브리핑은 임상 연구자를 위해 AI 파이프라인에 의해 분할/조립 자동 생성되었습니다.<br>
                    Generated by <b>Rehab Multi-Bots</b> on {current_date}
                </div>
            </div>
        </body>
        </html>
        """

        # 📱 [TRACK 3] 텔레그램 전용 프리미엄 미니 대시보드
        tldr_text = "- 이번 달 심층 브리핑이 성공적으로 생성되었습니다.\n- 이메일에서 상세한 내용을 확인해 주세요."

        # 🚀 정규표현식 보완: 수평선(---)이나 다른 특수문자에 걸리지 않도록 안전하게 파싱
        tldr_match = re.search(r'###?\s*💡.*?(?:3줄|요약).*?\n(.*?)(?=\n###? |\n---|---\n|\Z)', ai_md_report, re.DOTALL | re.IGNORECASE)
        if tldr_match:
            raw_tldr = tldr_match.group(1).strip()
            safe_tldr = raw_tldr.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            safe_tldr = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_tldr)
            safe_tldr = re.sub(r'\*(.*?)\*', r'<i>\1</i>', safe_tldr)
            safe_tldr = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', safe_tldr)
            tldr_text = safe_tldr

        top_3_html = ""
        for i, p in enumerate(ai_analysis_payload[:3], 1):
            safe_title = p['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            safe_journal = p['journal'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            top_3_html += f"<b>{i}위.</b> <a href='{p['doi']}'>{safe_title}</a>\n(<i>{safe_journal}</i> / 📈 {p['count']}회)\n\n"

        now_dt = datetime.now()
        kor_name_no_space = config.BOT_KOR_NAME.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(',', '')
        hashtags = f"#RehabBot #{kor_name_no_space} #DeepDive"

        tg_msg = f"""🚨 <b>[{config.BOT_KOR_NAME}] 1:1 심층 브리핑 도착!</b>
📊 <b>수집 개요:</b> 총 {total_papers}편 전체 딥다이브 해부 완료

💡 <b>이번 달 AI 3줄 요약</b>
{tldr_text}

🥇 <b>Top 3 주목받은 대장 논문</b>
{top_3_html.strip()}

💌 <i>수백 편의 1:1 논문 인용 가이드와 구체적 후속 연구 프로토콜은 이메일/옵시디언을 확인해 주세요!</i>

{hashtags}"""

        notify_all(f"🚀 [AI 1:1 심층 브리핑] {config.BOT_KOR_NAME} 도착", tg_msg, final_email_html, md_filename=md_filename, md_content=final_md_content)
        log.info(f"✅ 신규 Zotero 저장 및 리포트 발송 완료 (옵시디언 첨부파일: {md_filename})")
    else:
        log.info("이번 스캔에서 분석할 논문이 없습니다.")

def job_condition():
    db = DBManager()
    now = datetime.now()
    current_year_month_str = now.strftime("%Y-%m")
    if now.month != config.RUN_MONTH: return
    if db.get_setting("last_run_month") == current_year_month_str: return
    try:
        run_pipeline()
        db.set_setting("last_run_month", current_year_month_str)
    except Exception as e: log.error(f"실행 오류: {e}")

if __name__ == "__main__":
    job_condition()
    schedule.every().day.at("06:30").do(job_condition)
    while True:
        schedule.run_pending()
        time.sleep(60)
