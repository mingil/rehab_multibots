import sqlite3
import config
from logger import log

class DBManager:
    def __init__(self):
        self.db_path = config.DB_FILE
        self._create_table()

    def _create_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS papers (
                        ref_id TEXT PRIMARY KEY,
                        title TEXT,
                        year TEXT,
                        abstract TEXT,
                        doi TEXT,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        except Exception as e:
            log.error(f"DB 초기화 에러: {e}")

    def get_paper(self, ref_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT title, year, abstract, doi FROM papers WHERE ref_id=?", (ref_id,))
                row = cursor.fetchone()
                if row: return dict(row)
                return None
        except Exception as e:
            log.error(f"DB 조회 에러 ({ref_id}): {e}")
            return None

    def save_paper(self, ref_id, title, year, abstract, doi):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO papers (ref_id, title, year, abstract, doi)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ref_id, title, year, abstract, doi))
        except Exception as e:
            log.error(f"DB 저장 에러 ({ref_id}): {e}")
