import logging

log = logging.getLogger(__name__)

def telegram_html_escape(string: str):
    return string.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("&", "&amp;") \
        .replace('"', "&quot;")

def get_key(d, value):
    for k, v in d:
        log.debug(f"finding key: {v}")
        if v == value:
            return k
    return None
