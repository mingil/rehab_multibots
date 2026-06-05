import time
from google import genai
from google.genai import types
import config
from logger import log

def analyze_papers(papers_data):
    if not config.GEMINI_API_KEY: return "Gemini API 키가 설정되지 않아 분석이 생략되었습니다."
    try: client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e: return f"AI 초기화 오류: {e}"

    paper_text = ""
    for i, p in enumerate(papers_data, 1):
        abstract = p.get('abstract', '')
        if abstract and len(abstract) > 600: abstract = abstract[:600] + "..."
        # 🚀 DOI 링크를 함께 넘겨주어 본문에 다이렉트 링크를 달게 강제합니다.
        paper_text += f"[{p.get('rank', i)}위] 제목: {p['title']} ({p['year']})\nDOI: {p['doi']}\n초록: {abstract}\n\n"

    prompt_common = """
        [작성 가이드라인 - 필수 엄수!]
        1. 💡 3줄 요약 (TL;DR): 브리핑의 가장 첫 부분에 반드시 `### 💡 이번 달 AI 3줄 요약` 이라는 제목을 달고, 전체 트렌드를 관통하는 핵심 내용 3가지를 글머리 기호(`- `)를 사용하여 정확히 3줄로 작성하세요.
        2. 🔗 논문 제목 다이렉트 하이퍼링크 (가장 중요): 본문에서 개별 논문을 소개할 때는 절대 텍스트만 적지 마세요. 무조건 `[논문 제목](DOI 링크)` 형태의 마크다운 하이퍼링크를 적용하세요! (예시: [The PRISMA 2020 statement](https://doi.org/10.1136/bmj.n71) )
        3. 🚀 병원 임상 데이터를 활용해 전공의가 당장 시도해 볼 만한 독창적 '가성비' 후속 연구 아이디어 3가지 제안.
        4. 🚨 형식: 완벽한 순수 마크다운(Markdown) 문법(`#`, `**`, `-`, `[텍스트](URL)`)만 사용.
        5. 🚨 금지사항: 인삿말, 서론에서 저널의 권위를 주관적으로 평가하는 문구는 절대 쓰지 마세요 (시스템이 별도 표로 증명합니다). 맨 마지막에 원본 논문 리스트를 중복 나열하지 마세요.
    """

    if config.BOT_NAME == "ai":
        prompt = f"당신은 의료 인공지능(AI) 분야의 탁월한 연구 지도교수입니다. 아래 피인용 논문들의 데이터를 목적/알고리즘별로 세련되게 분류하세요.\n{prompt_common}\n[수집 논문]\n{paper_text}"
    else:
        prompt = f"당신은 **[{config.BOT_KOR_NAME}]** 분야의 최고 권위자입니다. 아래 논문들을 방법론과 세부 질환별로 스마트하게 분류하고 근거 활용 팁을 제시하세요.\n{prompt_common}\n[수집 논문]\n{paper_text}"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"🤖 Gemini API 분석 요청 중... (시도 {attempt}/{max_retries})")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7, safety_settings=[types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE")])
            )
            log.info("✅ Gemini API 스마트 분석 완료!")
            if not response.text: return "AI 분석 결과가 비어 있습니다."
            return response.text.replace("```markdown\n", "").replace("```\n", "").replace("```", "").strip()
        except Exception as e:
            if attempt < max_retries: time.sleep(15)
            else: return f"AI 분석 리포트 생성 중 오류 발생: {e}"
