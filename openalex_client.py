import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import Counter
import config

# 🛡️ 강력한 API 방어막 (Retry & Backoff 로직)
def get_retry_session():
    session = requests.Session()
    # 500번대 서버 에러와 429(Too Many Requests) 발생 시 총 3번 자동 재시도
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_openalex_headers():
    """Polite Pool 이메일과 Premium API Key를 함께 장착하여 쾌속/안정 수집을 보장합니다."""
    headers = {}
    if config.OPENALEX_EMAIL:
        headers["User-Agent"] = f"mailto:{config.OPENALEX_EMAIL}"

    # 🌟 API Key가 있다면 Authorization 헤더에 추가 (OpenAlex 공식 가이드 권장 방식)
    if hasattr(config, 'OPENALEX_API_KEY') and config.OPENALEX_API_KEY:
        headers["Authorization"] = f"Bearer {config.OPENALEX_API_KEY}"

    return headers

def get_top_citations(bot_cfg, start_year, end_year, top_n, log):
    headers = get_openalex_headers()
    domain = "api.openalex.org"
    base_url = f"https://{domain}/works"

    filters = f"primary_location.source.issn:{bot_cfg['target_issns']},publication_year:{start_year}-{end_year}"
    if bot_cfg.get('ai_search_keywords'):
        filters += f",title_and_abstract.search:{bot_cfg['ai_search_keywords']}"

    url = f"{base_url}?filter={filters}&select=referenced_works&per-page=200&cursor=*"
    all_refs = []
    cursor = "*"
    session = get_retry_session()

    while cursor:
        try:
            req_url = url.replace("cursor=*", f"cursor={cursor}")

            # 🔥 통신 멈춤(Hang) 방지: 연결 10초, 데이터 수신 30초가 넘어가면 예외 발생!
            res = session.get(req_url, headers=headers, timeout=(10, 30))

            if res.status_code != 200:
                log.warning(f"OpenAlex API 상태 코드 에러 ({res.status_code})")
                break

            data = res.json()
            if not data.get("results"): break

            for work in data["results"]:
                all_refs.extend(work.get("referenced_works", []))

            cursor = data.get("meta", {}).get("next_cursor")

            # API 키가 있으면 제한이 대폭 완화되므로 딜레이를 0.01초로 쾌속 진행합니다.
            time.sleep(0.01 if hasattr(config, 'OPENALEX_API_KEY') and config.OPENALEX_API_KEY else 0.1)

        except requests.exceptions.Timeout:
            log.warning("OpenAlex 서버 타임아웃(응답 지연) 발생. 현재까지 수집된 데이터만 반환합니다.")
            break
        except Exception as e:
            log.warning(f"OpenAlex API 인용 목록 수집 중 오류: {e}")
            break

    return Counter(all_refs).most_common(top_n)

def reconstruct_abstract(abs_idx):
    """OpenAlex의 역색인(abstract_inverted_index) 데이터를 평문 초록으로 복원합니다."""
    if not abs_idx or not isinstance(abs_idx, dict):
        return ""
    try:
        positions = [max(pos) for pos in abs_idx.values() if pos]
        if not positions:
            return ""
        max_idx = max(positions)
        words = [""] * (max_idx + 1)
        for w, p_list in abs_idx.items():
            if not p_list:
                continue
            for p in p_list:
                words[p] = w
        return " ".join(words).strip()
    except Exception:
        return ""

def fetch_paper_meta(ref_id, log):
    headers = get_openalex_headers()
    work_id = ref_id.split("/")[-1]
    api_url = f"https://api.openalex.org/works/{work_id}"
    session = get_retry_session()

    try:
        # 🔥 단일 메타데이터 조회는 더 타이트하게 제한 (연결 5초, 수신 15초)
        res = session.get(api_url, headers=headers, timeout=(5, 15))
        if res.status_code != 200: return None
        data = res.json()

        journal = "Unknown Journal"
        if data.get("primary_location") and data["primary_location"].get("source"):
            journal = data["primary_location"]["source"].get("display_name", "Unknown Journal")

        authorships = data.get("authorships", [])
        author_names = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author", {}).get("display_name")]
        if len(author_names) > 2: authors_str = f"{author_names[0]} et al."
        elif author_names: authors_str = ", ".join(author_names)
        else: authors_str = "Unknown Authors"

        abstract_text = reconstruct_abstract(data.get("abstract_inverted_index"))

        study_design = "Original Research"
        title_abs = (str(data.get("title") or "") + " " + abstract_text).lower()
        work_type = str(data.get("type") or "").lower()
        concepts = [str(c.get("display_name") or "").lower() for c in data.get("concepts", [])]

        if "meta-analysis" in concepts or "systematic review" in concepts or "meta-analysis" in title_abs or "systematic review" in title_abs:
            study_design = "Systematic Review & Meta-analysis"
        elif "randomized controlled trial" in concepts or "randomized" in title_abs or "rct" in title_abs.split():
            study_design = "Randomized Controlled Trial (RCT)"
        elif "guideline" in concepts or "guideline" in title_abs or "consensus" in title_abs:
            study_design = "Clinical Guideline / Consensus"
        elif "cohort" in concepts or "cohort" in title_abs:
            study_design = "Cohort Study"
        elif "case-control" in concepts or "case control" in title_abs:
            study_design = "Case-Control Study"
        elif "review" in work_type:
            study_design = "Review Article"
        elif "case report" in concepts or "case report" in title_abs:
            study_design = "Case Report"

        data["_journal"] = journal
        data["_authors"] = authors_str
        data["_study_design"] = study_design
        data["_abstract"] = abstract_text

        return data

    except requests.exceptions.Timeout:
        # 타임아웃 발생 시 멈추지 않고 조용히 None 반환 후 다음 논문으로 넘어감
        log.warning(f"메타데이터 수집 타임아웃 ({ref_id})")
        return None
    except Exception as e:
        log.error(f"메타데이터 수집 에러 ({ref_id}): {e}")
        return None
