import time
import requests
from collections import Counter
import config
from logger import log

def get_top_citations(start_year, end_year, top_n):
    headers = {"User-Agent": f"mailto:{config.OPENALEX_EMAIL}"} if config.OPENALEX_EMAIL else {}
    
    # 마크다운 자동 변환 방지를 위한 URL 안전 분리
    domain = "api.openalex.org"
    base_url = f"https://{domain}/works"
    filters = f"primary_location.source.issn:{config.TARGET_ISSNS},publication_year:{start_year}-{end_year}"
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
