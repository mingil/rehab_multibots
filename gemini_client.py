import json
import re
import time
from google import genai
from google.genai import types
import config

def call_gemini(prompt, client, log, use_json=False):
    max_retries = 3
    config_dict = {
        "temperature": 0.2 if use_json else 0.7,
        "safety_settings": [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE")
        ]
    }
    if use_json:
        config_dict["response_mime_type"] = "application/json"

    cfg = types.GenerateContentConfig(**config_dict)

    primary_model = getattr(config, "GEMINI_MODEL", "gemini-3.8-flash")
    fallback_models = getattr(config, "GEMINI_FALLBACK_MODELS", ["gemini-3.6-flash", "gemini-3.5-flash-lite"])
    model_candidates = [primary_model] + [m for m in fallback_models if m != primary_model]

    for model_name in model_candidates:
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    # 🔥 최고 가성비 모델(기본값: gemini-3.8-flash)로 호출하며, 서버 과부하 시 하위 모델로 자동 폴백합니다.
                    model=model_name,
                    contents=prompt,
                    config=cfg
                )
                if response.text:
                    text = response.text.strip()
                    if use_json:
                        text = re.sub(r'^```json\n?', '', text, flags=re.IGNORECASE)
                        text = re.sub(r'```$', '', text).strip()
                    else:
                        text = text.replace("```markdown\n", "").replace("```\n", "").replace("```", "").strip()
                    return text
                return ""
            except Exception as e:
                wait_sec = 15 * attempt
                log.warning(f"Gemini API 에러 [{model_name}] (시도 {attempt}/{max_retries}): {e} -> {wait_sec}초 대기")
                if attempt < max_retries:
                    time.sleep(wait_sec)
                else:
                    log.warning(f"⚠️ [{model_name}] 응답 실패. 다음 백업 모델로 자동 전환을 시도합니다.")
    return ""

def analyze_papers(papers_data, log):
    if not config.GEMINI_API_KEY: return "Gemini API 키가 설정되지 않아 분석이 생략되었습니다."
    try: client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e: return f"AI 초기화 오류: {e}"

    total_count = len(papers_data)
    log.info(f"🤖 총 {total_count}편 논문 2-Phase 하이브리드 엔진 가동 (숲 기획 -> 나무 분석)")

    paper_dict = {p.get('rank', i+1): p for i, p in enumerate(papers_data)}
    lite_papers = [{"id": p['rank'], "title": p['title'], "abstract": p.get('abstract', '')[:300]} for p in papers_data]

    prompt_phase1 = f"""
    당신은 재활의학과 및 의료 인공지능 분야의 최고 권위자이자 학술 편집장입니다.
    아래 제공된 총 {total_count}편의 논문 리스트를 보고 임상적 주제에 따라 4~6개의 스마트한 카테고리로 완벽하게 분류하세요.
    모든 논문(ID 기준)은 반드시 하나의 카테고리에 할당되어야 합니다 (누락 절대 금지).

    반드시 아래 JSON 스키마 구조와 정확히 일치하게 응답하세요.

    {{
      "tldr": [
        "전체 트렌드를 관통하는 핵심 내용 1",
        "전체 트렌드 내용 2",
        "전체 트렌드 내용 3"
      ],
      "categories": [
        {{
          "title": "카테고리명 (예: 뇌졸중 후 로봇 보행 재활)",
          "intro": "이 카테고리 연구들의 임상적 중요성과 최근 동향을 설명하는 2~3문장의 미니 총평.",
          "tags": "#로봇재활 #보행치료 #뇌졸중",
          "paper_ids": [1, 5, 12]
        }}
      ],
      "protocols": [
        {{
          "title": "전공의 후속 연구 아이디어 제목",
          "data": "필요한 병원 EMR/영상 데이터",
          "method": "분석 방법론",
          "gap": "타겟팅할 틈새 및 한계 극복 방안"
        }}
      ]
    }}

    [분석할 논문 리스트 데이터]
    {json.dumps(lite_papers, ensure_ascii=False)}
    """

    log.info(" -> 1/2단계: [편집장] 카테고리 맵핑 및 미니 총평(Intro) 기획 중...")
    raw_json = call_gemini(prompt_phase1, client, log, use_json=True)

    try:
        blueprint = json.loads(raw_json)
    except Exception as e:
        log.error(f"JSON 파싱 에러, 안전망으로 전환합니다: {e}")
        blueprint = {
            "tldr": ["전체 트렌드 분석을 성공적으로 마쳤습니다.", "하위 상세 분석을 확인하세요.", "수집된 논문 전수 분석입니다."],
            "categories": [{"title": "통합 임상 연구", "tags": "#통합리뷰", "intro": "이번 달 전체 주요 연구입니다.", "paper_ids": list(paper_dict.keys())}],
            "protocols": []
        }

    final_report = "### 💡 이번 달 AI 3줄 요약\n"
    for line in blueprint.get("tldr", []):
        final_report += f"- {line}\n"
    final_report += "\n---\n\n"

    categories = blueprint.get("categories", [])
    assigned_ranks = set()
    for cat in categories:
        assigned_ranks.update(cat.get("paper_ids", []))

    missing_ranks = [r for r in paper_dict.keys() if r not in assigned_ranks]
    if missing_ranks:
        categories.append({
            "title": "기타 주요 연구 동향",
            "tags": "#기타연구 #세부분석",
            "intro": "카테고리에 명확히 분류되지 않았으나, 임상적으로 주목할 만한 특수 질환 및 기타 논문들입니다.",
            "paper_ids": missing_ranks
        })

    for idx, cat in enumerate(categories, 1):
        cat_title = cat.get("title", "기타 트렌드")
        cat_intro = cat.get("intro", "")
        cat_tags = cat.get("tags", "")
        p_ranks = cat.get("paper_ids", [])

        cat_papers = [paper_dict[r] for r in p_ranks if r in paper_dict]
        if not cat_papers: continue

        final_report += f"## 📂 {idx}. {cat_title} <span style='color:#3b82f6; font-size:16px;'>{cat_tags}</span>\n"
        if cat_intro:
            final_report += f"> 💡 **미니 총평:** {cat_intro}\n\n"

        log.info(f" -> 2/2단계: [집필진] '{cat_title}' 카테고리 ({len(cat_papers)}편) 1:1 심층 해부 중...")

        for i in range(0, len(cat_papers), 20):
            chunk = cat_papers[i:i + 20]
            chunk_text = ""
            for p in chunk:
                abs_text = p.get('abstract', '')
                if abs_text and len(abs_text) > 600: abs_text = abs_text[:600] + "..."
                chunk_text += f"[{p.get('rank', 0)}위] 제목: {p['title']} ({p['year']})\nDOI: {p['doi']}\n초록: {abs_text}\n\n"

            prompt_phase2 = f"""
            당신은 '{cat_title}' 분야의 논문 지도교수입니다.
            아래 제공된 {len(chunk)}편의 논문을 **단 한 편도 빠짐없이 100% 모두** 분석하여 1:1 실전 인용 가이드를 작성하세요.
            (인삿말이나 서론 없이 바로 리스트만 마크다운으로 출력하세요)

            [필수 포맷 - 3단 포맷을 반드시 지키고 1~2문장으로 압축할 것]
            - **[논문 제목](원본 DOI 링크)** (반드시 논문 제목에 마크다운 하이퍼링크 적용)
              - 💡 **핵심 발견:** 이 연구가 증명한 가장 중요한 팩트.
              - 🎯 **실전 인용 팁:** 내 논문의 서론, 방법, 고찰 중 어디에 어떤 근거로 인용할지 구체적 가이드.
              - ⚠️ **연구 공백:** 한계점이나 후속 연구를 위한 아쉬운 틈새.

            [논문 데이터]
            {chunk_text}
            """
            final_report += call_gemini(prompt_phase2, client, log, use_json=False) + "\n\n"
            time.sleep(3)

        final_report += "---\n\n"

    protocols = blueprint.get("protocols", [])
    if protocols:
        final_report += "### 🚀 전공의를 위한 후속 연구 미니-프로토콜\n\n"
        for i, proto in enumerate(protocols, 1):
            final_report += f"#### {i}. {proto.get('title', '연구 주제')}\n"
            final_report += f"- 📊 **필요 데이터:** {proto.get('data', '')}\n"
            final_report += f"- 🛠️ **분석 방법론:** {proto.get('method', '')}\n"
            final_report += f"- 🎯 **타겟팅할 틈새:** {proto.get('gap', '')}\n\n"

    log.info("✅ 2-Phase [카테고리 + 1:1 딥다이브] 조립 완벽 종료!")
    return final_report.strip()
