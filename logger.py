import logging
import sys
from logging.handlers import RotatingFileHandler
import config

formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger(config.BOT_NAME)
log.setLevel(logging.INFO)

if not log.handlers:
    # 1. 터미널 출력용 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # 2. 파일 저장용 핸들러 (🚀 최대 5MB 유지, 오래된 로그 3개까지만 백업하고 알아서 삭제)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5 * 1024 * 1024, # 5MB limit
        backupCount=3,            # Keep 3 backups
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
