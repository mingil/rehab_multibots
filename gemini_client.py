import time
import re
from google import genai
from google.genai import types
import config
from logger import log

def call_gemini(prompt, client):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE")
                    ]
                )
            )
            if response.text:
                return response.text.replace("```markdown\n", "").replace("```\n", "").replace("```", "").strip()
            return ""
        except Exception as e:
            log.error(f"Gemini API 에러 (시도 {attempt}): {e}")
            if attempt < max_retries: time.sleep(15)
            else: return f"AI 분석 오류: {e}"
    return ""

def analyze_papers(papers_data):
    if not config.GEMINI_API_KEY: return "Gemini API 키가 설정되지 않아 분석이 생략되었습니다."
    try: client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e: return f"AI 초기화 오류: {e}"

    total_count = len(papers_data)
    log.info(f"🤖 총 {total_count}편 논문 전수 1:1 정밀 분석 가동 (Chunking 분할 기법 적용)")

    # ==============================================================
    # 🧠 [STEP 1] 전체 트렌드 3줄 요약 및 미니 프로토콜 기획
    # ==============================================================
    summary_text = ""
    for i, p in enumerate(papers_data, 1):
        summary_text += f"[{p.get('rank', i)}위] 제목: {p['title']} ({p['year']}) | 저널: {p.get('journal', 'Unknown')}\n"

    prompt_main = f"""
    당신은 재활의학과 및 의료 인공지능 분야의 최고 권위자입니다.
    아래는 이번 달에 수집된 총 {total_count}편의 메이저 논문 리스트입니다.

    [작성 가이드라인]
    1. 💡 3줄 요약 (TL;DR): 가장 먼저 `### 💡 이번 달 AI 3줄 요약` 이라는 제목을 달고, 이 분야의 전체 트렌드를 관통하는 핵심 내용 3가지를 글머리 기호(`- `)로 요약하세요.
    2. 🚀 후속 연구 미니-프로토콜 3선: 그 다음 줄에 `### 🚀 전공의를 위한 후속 연구 미니-프로토콜` 이라는 제목을 달고, 당장 병원에서 후향적 데이터로 시도해 볼 만한 독창적인 연구 아이디어 3가지를 제안하세요.
       - **[연구 주제명]**
         - 📊 **필요 데이터:** (예: EMR 텍스트, T1 MRI, 심전도 등 명확히)
         - 🛠️ **분석 방법론:** (예: 생존 분석, 딥러닝 CNN, 성향점수매칭 등)
         - 🎯 **타겟팅할 틈새:** (이전 족보 논문들의 한계를 어떻게 극복하는지)

    [수집 논문 리스트]
    {summary_text}
    """

    log.info(" -> 1/2단계: 전체 트렌드 분석 및 후속 연구 프로토콜 생성 중...")
    main_insight = call_gemini(prompt_main, client)

    # ==============================================================
    # 🧠 [STEP 2] 청킹(Chunking)을 통한 개별 논문 100% 전수 1:1 해부
    # ==============================================================
    chunk_size = 30
    chunks = [papers_data[i:i + chunk_size] for i in range(0, total_count, chunk_size)]

    micro_reviews = ""
    for idx, chunk in enumerate(chunks, 1):
        log.info(f" -> 2/2단계: 논문 1:1 해부 청크 {idx}/{len(chunks)} 진행 중...")
        chunk_text = ""
        for p in chunk:
            abs_text = p.get('abstract', '')
            if abs_text and len(abs_text) > 600: abs_text = abs_text[:600] + "..."
            chunk_text += f"[{p.get('rank', 0)}위] 제목: {p['title']} ({p['year']})\nDOI: {p['doi']}\n초록: {abs_text}\n\n"

        prompt_chunk = f"""
        당신은 탁월한 논문 지도교수입니다.
        아래 제공된 {len(chunk)}편의 논문을 **단 한 편도 빠짐없이 100% 모두** 분석하여 1:1 실전 인용 가이드를 작성하세요.

        [필수 포맷 - 반드시 모든 논문에 대해 아래 3단 포맷을 적용하여 1~2문장으로 압축할 것]
        - **[논문 제목](원본 DOI 링크)** (반드시 논문 제목에 마크다운 하이퍼링크 적용)
          - 💡 **핵심 발견:** 이 연구가 증명한 가장 중요한 팩트.
          - 🎯 **실전 인용 팁:** 내 논문의 서론, 대상 및 방법, 고찰 등에 어떤 근거로 인용할지 구체적인 가이드.
          - ⚠️ **연구 공백:** 이 연구가 다루지 못한 한계나 아쉬운 틈새.

        (서론이나 맺음말 없이, 오직 위 포맷에 맞춘 리스트만 출력하세요. 순수 마크다운만 사용하세요.)

        [분석할 논문 청크 데이터]
        {chunk_text}
        """
        chunk_res = call_gemini(prompt_chunk, client)
        micro_reviews += chunk_res + "\n\n"
        time.sleep(3) # API Rate Limit 보호

    # ==============================================================
    # 🧠 [STEP 3] 최종 리포트 조립 반환
    # ==============================================================
    log.info("✅ 1:1 딥다이브 전수 분석 완료! 최종 리포트 조립 중...")

    tldr_part = main_insight
    protocol_part = ""

    # AI가 앞서 작성한 미니 프로토콜 부분을 잘라내어 리포트 맨 밑으로 예쁘게 재배치합니다.
    parts = re.split(r'###\s*🚀\s*전공의를 위한 후속 연구 미니-프로토콜', main_insight, flags=re.IGNORECASE)
    if len(parts) >= 2:
        tldr_part = parts[0].strip()
        protocol_part = "### 🚀 전공의를 위한 후속 연구 미니-프로토콜\n" + parts[1].strip()

    final_report = f"{tldr_part}\n\n### 🔬 수집 논문 전수 1:1 실전 인용 가이드 (총 {total_count}편)\n\n{micro_reviews.strip()}\n\n---\n\n{protocol_part}"

    return final_report
