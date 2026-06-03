import logging
from logging.handlers import RotatingFileHandler
import sys
import config

def get_logger(name=config.BOT_NAME):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(f'[%(asctime)s] [{config.BOT_KOR_NAME}] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        try:
            fh = RotatingFileHandler(config.LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass
            
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

log = get_logger()
