import sqlite3
import os

class DBManager:
    def __init__(self, db_path: str, logger=None):
        self.db_path = db_path
        self.log = logger
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
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
                conn.execute('CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, val TEXT)')

                # 정석적인 DB 스키마 안전 확인 및 마이그레이션
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(papers)")
                columns = [col[1] for col in cursor.fetchall()]

                if 'journal' not in columns:
                    conn.execute("ALTER TABLE papers ADD COLUMN journal TEXT DEFAULT 'Unknown Journal'")
                if 'authors' not in columns:
                    conn.execute("ALTER TABLE papers ADD COLUMN authors TEXT DEFAULT 'Unknown Authors'")
                if 'study_design' not in columns:
                    conn.execute("ALTER TABLE papers ADD COLUMN study_design TEXT DEFAULT 'Original Research'")

        except Exception as e:
            if self.log: self.log.error(f"DB 초기화 에러: {e}")

    def get_paper(self, ref_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM papers WHERE ref_id=?", (ref_id,))
                row = cursor.fetchone()
                if row: return dict(row)
                return None
        except Exception:
            return None

    def save_paper(self, ref_id, title, year, abstract, doi, journal="Unknown Journal", authors="Unknown Authors", study_design="Original Research"):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO papers (ref_id, title, year, abstract, doi, journal, authors, study_design)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ref_id, title, year, abstract, doi, journal, authors, study_design))
        except Exception as e:
            if self.log: self.log.error(f"DB 저장 에러: {e}")

    def get_setting(self, key):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT val FROM bot_settings WHERE key=?", (key,))
                row = cursor.fetchone()
                if row: return row[0]
                return None
        except Exception:
            return None

    def set_setting(self, key, val):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT OR REPLACE INTO bot_settings (key, val) VALUES (?, ?)", (key, val))
        except Exception:
            pass
