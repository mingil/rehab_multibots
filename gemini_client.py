import time
import google.generativeai as genai
import config
from logger import log

def extract_text_safely(response):
    try:
        return response.text
    except ValueError:
        text_parts = []
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
        result = "".join(text_parts)
        if not result.strip():
            return "AI 분석 결과가 안전 필터에 의해 차단되었거나 텍스트가 비어 있습니다."
        return result

def analyze_papers(papers_data):
    if not config.GEMINI_API_KEY:
        log.warning("Gemini API 키가 없습니다.")
        return "<h3>Gemini API 키가 설정되지 않아 AI 분석이 생략되었습니다.</h3>"

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]

    paper_text = ""
    for i, p in enumerate(papers_data, 1):
        abstract = p.get('abstract', '')
        if abstract and len(abstract) > 600:
            abstract = abstract[:600] + "..."
        paper_text += f"[{p.get('rank', i)}위] 제목: {p['title']} ({p['year']}) | 피인용: {p['count']}회\n초록: {abstract}\n\n"

    # 🤖 12월 AI 전용 프롬프트 분기
    if config.BOT_NAME == "ai":
        prompt = f"""
        당신은 재활의학과 최고 권위자이자 의료 인공지능(AI) 및 데이터 사이언스 분야의 탁월한 연구 지도교수입니다.
        아래는 재활의학 전 분야 메이저 저널들에서 출판된 '인공지능, 머신러닝, 딥러닝' 관련 피인용 최상위 논문 {len(papers_data)}편의 초록 요약입니다.

        임상 전공의가 코딩이나 AI의 복잡한 수학적 이론을 깊게 몰라도, 병원에 쌓여있는 임상 데이터(EMR, 영상, 신호 등)를 활용해 훌륭한 AI/ML 논문을 기획할 수 있도록 기획안을 작성해 주세요.

        [작성 가이드라인 - 매우 중요!]
        1. 📊 활용 데이터 및 알고리즘 목적별 분류: 논문들을 단순히 질환별로 나누지 말고, [분석한 데이터 종류 (예: MRI/초음파/X-ray 영상, 보행/웨어러블 센서, 뇌파/근전도 생체신호, EMR 텍스트 등)]와 [AI 알고리즘의 임상적 목적 (자동 진단, 예후 및 기능회복 예측, 맞춤형 치료 추천 등)]에 따라 세련되게 카테고리화 하세요.
        2. 🩺 임상 활용 팁 및 트렌드 통찰: 각 카테고리 내 핵심 논문들이 기존의 통계적 방법론을 어떻게 뛰어넘었으며, 어떤 모델(CNN, LLM, XGBoost 등)을 썼는지 전공의 눈높이에서 쉽게 설명해 주세요.
        3. 🚀 당장 시도해 볼 만한 "가성비" 후속 연구 아이디어(Research Gap): 위 트렌드를 종합하여, 수련병원 전공의가 (1) 복잡한 코딩 없이 접근 가능하거나, (2) 병원에 이미 축적된 후향적 데이터를 활용하여 당장 시도해 볼 만한 '가성비 높고 독창적인 임상 AI 후속 연구 아이디어 3가지'를 구체적(필요 데이터 셋, 예상 모델, 임상적 가치)으로 제안해 주세요.
        4. 형식: 전문적이고 자연스러운 한국어. 가독성 좋은 HTML 태그(<h2>, <h3>, <ul>, <li>, <b> 등)만 사용하여 출력 (마크다운 억음부호 절대 금지).

        [수집된 방대한 논문 데이터]
        {paper_text}
        """
    else:
        # 🩺 기존 1~11월 일반 분과 프롬프트
        prompt = f"""
        당신은 재활의학과 최고 권위자이자 탁월한 논문 지도교수입니다.
        아래는 재활의학 세부분과 중 **[{config.BOT_KOR_NAME}]** 분야 최상위 저널들에서 가장 많이 인용된 족보 논문 {len(papers_data)}편의 초록 요약입니다.
        이 거대한 리스트 안에는 체계적 문헌고찰 가이드라인(PRISMA 등), 통계학 방법론 논문, 범용 평가 척도 논문들이 다수 섞여 있을 수 있습니다.

        전공의가 논문을 쉽게 기획하고 인용(Citation)할 수 있도록, 이 {len(papers_data)}편을 스마트하게 구조화하고 기획안을 작성해 주세요.

        [작성 가이드라인 - 매우 중요!]
        1. 💡 기초 방법론 및 척도 격리: 통계학, 문헌고찰 가이드라인(PRISMA 등), 범용 평가 척도 논문들은 모조리 <1. 기초 방법론 및 필수 평가 척도> 카테고리로 묶어 분리 수용하세요.
        2. 🩺 임상 세부 주제별 스마트 분류: 방법론을 제외한 나머지 '진짜 임상/연구 논문'들을 **[{config.BOT_KOR_NAME}]** 분야의 특성에 맞게 세부 질환이나 치료법별로 카테고리화 하세요.
        3. 논문 활용 팁: 각 임상 카테고리 내 핵심 논문들을 언급하며 서론이나 고찰 작성 시 어떤 근거로 활용할 수 있을지 구체적인 팁을 주세요.
        4. 💡 후속 연구 아이디어(Research Gap): 위 논문들의 메가 트렌드를 종합하여, 실제 병원의 임상 데이터를 활용해 전공의가 당장 시도해 볼 만한 독창적인 **[{config.BOT_KOR_NAME}]** 관련 후속 연구 아이디어 3가지를 매우 구체적으로 제안해 주세요.
        5. 형식: 전문적이고 자연스러운 한국어. 가독성 좋은 HTML 태그(<h2>, <h3>, <ul>, <li>, <b> 등)만 사용하여 출력 (마크다운 억음부호 절대 금지).

        [수집된 방대한 논문 데이터]
        {paper_text}
        """

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"🤖 Gemini API 분석 요청 중... (시도 {attempt}/{max_retries}, 최대 10분 대기)")
            response = model.generate_content(
                prompt,
                request_options={"timeout": 600},
                safety_settings=safety_settings
            )
            safe_text = extract_text_safely(response)
            log.info("✅ Gemini API 스마트 분석 완료!")
            return safe_text.replace("```html", "").replace("```", "").strip()

        except Exception as e:
            log.error(f"Gemini API 에러 (시도 {attempt}): {e}")
            if attempt < max_retries:
                time.sleep(15)
            else:
                return f"<p>AI 분석 리포트 생성 중 오류가 발생했습니다. (최종 실패: {e})</p>"
