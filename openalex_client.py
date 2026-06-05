import time
import requests
from collections import Counter
import config
from logger import log

def get_top_citations(start_year, end_year, top_n):
    headers = {"User-Agent": f"mailto:{config.OPENALEX_EMAIL}"} if config.OPENALEX_EMAIL else {}
    domain = "api.openalex.org"
    base_url = f"https://{domain}/works"
    filters = f"primary_location.source.issn:{config.TARGET_ISSNS},publication_year:{start_year}-{end_year}"
    if config.AI_SEARCH_KEYWORDS: filters += f",title_and_abstract.search:{config.AI_SEARCH_KEYWORDS}"

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
            for work in data["results"]: all_refs.extend(work.get("referenced_works", []))
            cursor = data.get("meta", {}).get("next_cursor")
            time.sleep(0.1)
        except: break
    return Counter(all_refs).most_common(top_n)

def fetch_paper_meta(ref_id):
    headers = {"User-Agent": f"mailto:{config.OPENALEX_EMAIL}"} if config.OPENALEX_EMAIL else {}
    work_id = ref_id.split("/")[-1]
    api_url = f"https://api.openalex.org/works/{work_id}"

    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code != 200: return None
        data = res.json()

        # 1. 딥 파싱: 저널명 추출
        journal = "Unknown Journal"
        if data.get("primary_location") and data["primary_location"].get("source"):
            journal = data["primary_location"]["source"].get("display_name", "Unknown Journal")

        # 2. 딥 파싱: 대표 저자명 (First Author et al.)
        authorships = data.get("authorships", [])
        author_names = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author", {}).get("display_name")]
        if len(author_names) > 2: authors_str = f"{author_names[0]} et al."
        elif author_names: authors_str = ", ".join(author_names)
        else: authors_str = "Unknown Authors"

        # 3. 딥 파싱: 연구 설계(Study Design) 유추
        study_design = "Original Research"
        title_abs = str(data.get("title", "")) + " " + str(data.get("abstract", ""))
        title_abs = title_abs.lower()
        work_type = str(data.get("type", "")).lower()
        concepts = [str(c.get("display_name", "")).lower() for c in data.get("concepts", [])]

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

        return data
    except Exception as e:
        log.error(f"메타데이터 수집 에러 ({ref_id}): {e}")
        return None
