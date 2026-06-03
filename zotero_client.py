from pyzotero import zotero
import config
from logger import log

class ZoteroClient:
    def __init__(self):
        if not config.ZOTERO_USER_ID or not config.ZOTERO_API_KEY:
            self.zot = None
            log.warning("Zotero API 정보가 누락되었습니다.")
        else:
            self.zot = zotero.Zotero(config.ZOTERO_USER_ID, 'user', config.ZOTERO_API_KEY)
        self.folder_id = config.ZOTERO_FOLDER_ID

    def is_duplicate(self, clean_doi):
        if not self.zot or not clean_doi: return False
        try:
            return len(self.zot.items(q=clean_doi)) > 0
        except Exception:
            return False

    def save_paper(self, meta, count):
        if not self.zot: return None
        
        doi_url = meta.get("doi") or ""
        doi_domain = "doi.org"
        clean_doi = doi_url.replace(f"https://{doi_domain}/", "") if doi_url else ""
        title = (meta.get("title") or "No Title").replace("<", "").replace(">", "")
        pub_year = str(meta.get("publication_year", ""))
        
        abstract_text = ""
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
            except: pass

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
            
        try:
            self.zot.create_items([template])
            paper_data["status"] = "added"
            return paper_data
        except Exception as e:
            log.error(f"Zotero 저장 에러: {e}")
            return None
