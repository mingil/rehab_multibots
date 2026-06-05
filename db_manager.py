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
                conn.execute('CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, val TEXT)')

                # 기존 DB에 컬럼 안전 추가 (이미 존재하면 에러 없이 넘어감)
                try: conn.execute("ALTER TABLE papers ADD COLUMN journal TEXT DEFAULT 'Unknown Journal'")
                except: pass
                try: conn.execute("ALTER TABLE papers ADD COLUMN authors TEXT DEFAULT 'Unknown Authors'")
                except: pass
                try: conn.execute("ALTER TABLE papers ADD COLUMN study_design TEXT DEFAULT 'Original Research'")
                except: pass

        except Exception as e:
            log.error(f"DB 초기화 에러: {e}")

    def get_paper(self, ref_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM papers WHERE ref_id=?", (ref_id,))
                row = cursor.fetchone()
                if row: return dict(row)
                return None
        except Exception as e:
            return None

    def save_paper(self, ref_id, title, year, abstract, doi, journal="Unknown Journal", authors="Unknown Authors", study_design="Original Research"):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO papers (ref_id, title, year, abstract, doi, journal, authors, study_design)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ref_id, title, year, abstract, doi, journal, authors, study_design))
        except Exception as e:
            log.error(f"DB 저장 에러: {e}")

    def get_setting(self, key):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT val FROM bot_settings WHERE key=?", (key,))
                row = cursor.fetchone()
                if row: return row[0]
                return None
        except Exception as e:
            return None

    def set_setting(self, key, val):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT OR REPLACE INTO bot_settings (key, val) VALUES (?, ?)", (key, val))
        except Exception as e:
            pass
