import time
from pyzotero import zotero
import config

class ZoteroClient:
    def __init__(self, bot_cfg, log):
        self.log = log
        if not config.ZOTERO_USER_ID or not config.ZOTERO_API_KEY:
            self.zot = None
            self.log.warning("Zotero API 정보가 누락되었습니다.")
        else:
            self.zot = zotero.Zotero(config.ZOTERO_USER_ID, 'user', config.ZOTERO_API_KEY)

        self.folder_id = bot_cfg.get("zotero_folder_id")

    def is_duplicate(self, clean_doi):
        if not self.zot or not clean_doi: return False

        # 🛡️ 3회 재시도 방어막
        for attempt in range(3):
            try:
                return len(self.zot.items(q=clean_doi)) > 0
            except Exception as e:
                if attempt == 2:
                    self.log.warning(f"Zotero 중복 검사 3회 실패 ({clean_doi}): {e}")
                    return False
                time.sleep(2)
        return False

    def save_paper(self, meta, count):
        if not self.zot: return None

        doi_url = meta.get("doi") or ""
        doi_domain = "doi.org"
        clean_doi = doi_url.replace(f"https://{doi_domain}/", "") if doi_url else ""
        title = (meta.get("title") or "No Title").replace("<", "").replace(">", "")
        pub_year = str(meta.get("publication_year", ""))

        abstract_text = meta.get("_abstract") or ""
        if not abstract_text:
            abs_idx = meta.get('abstract_inverted_index') or {}
            if abs_idx:
                try:
                    positions = [max(pos) for pos in abs_idx.values() if pos]
                    if positions:
                        max_idx = max(positions)
                        words = [""] * (max_idx + 1)
                        for w, p_list in abs_idx.items():
                            if not p_list: continue
                            for p in p_list: words[p] = w
                        abstract_text = " ".join(words).strip()
                except Exception:
                    pass

        paper_data = {"title": title, "year": pub_year, "count": count, "abstract": abstract_text, "doi": doi_url}

        if self.is_duplicate(clean_doi):
            paper_data["status"] = "duplicate"
            return paper_data

        template = self.zot.item_template('journalArticle')
        template['title'] = title
        template['DOI'] = clean_doi
        template['url'] = doi_url
        template['date'] = pub_year
        template['abstractNote'] = abstract_text

        try: template['publicationTitle'] = meta.get('primary_location', {}).get('source', {}).get('display_name', '')
        except: pass

        authors = []
        for auth in meta.get('authorships', [])[:10]:
            name = (auth.get('author', {}).get('display_name') or '').split()
            if len(name) > 1: authors.append({"creatorType": "author", "firstName": " ".join(name[:-1]), "lastName": name[-1]})
            elif name: authors.append({"creatorType": "author", "lastName": name[0]})
        template['creators'] = authors

        if self.folder_id:
            template['collections'] = [self.folder_id]

        # 🛡️ 3회 재시도 방어막
        for attempt in range(3):
            try:
                self.zot.create_items([template])
                paper_data["status"] = "added"
                return paper_data
            except Exception as e:
                if attempt == 2:
                    self.log.error(f"Zotero 저장 최종 실패: {title[:30]}... ({e})")
                    return None
                time.sleep(3)
