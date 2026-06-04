import time
import requests
from collections import Counter
import config
from logger import log

def get_top_citations(start_year, end_year, top_n):
    headers = {"User-Agent": f"mailto:{config.OPENALEX_EMAIL}"} if config.OPENALEX_EMAIL else {}

    domain = "api.openalex.org"
    base_url = f"https://{domain}/works"

    # 1. 기본 필터: 지정된 재활 저널 목록(ISSN) 및 출판 연도
    filters = f"primary_location.source.issn:{config.TARGET_ISSNS},publication_year:{start_year}-{end_year}"

    # 2. 12월 AI 봇일 경우 제목/초록에 키워드 검색 필터 추가
    if config.AI_SEARCH_KEYWORDS:
        filters += f",title_and_abstract.search:{config.AI_SEARCH_KEYWORDS}"

    url = f"{base_url}?filter={filters}&select=referenced_works&per-page=200&cursor=*"

    all_refs = []
    cursor = "*"
    while cursor:
        try:
            req_url = url.replace("cursor=*", f"cursor={cursor}")
            res = requests.get(req_url, headers=headers, timeout=30)
            if res.status_code != 200: break
            data = res.json()
            if not data.get("results"): break
            for work in data["results"]:
                all_refs.extend(work.get("referenced_works", []))
            cursor = data.get("meta", {}).get("next_cursor")
            time.sleep(0.1)
        except Exception as e:
            log.error(f"목록 수집 에러: {e}")
            break

    return Counter(all_refs).most_common(top_n)

def fetch_paper_meta(ref_id):
    headers = {"User-Agent": f"mailto:{config.OPENALEX_EMAIL}"} if config.OPENALEX_EMAIL else {}
    work_id = ref_id.split("/")[-1]

    domain = "api.openalex.org"
    api_url = f"https://{domain}/works/{work_id}"

    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code != 200: return None
        return res.json()
    except Exception as e:
        log.error(f"메타데이터 수집 에러 ({ref_id}): {e}")
        return None
