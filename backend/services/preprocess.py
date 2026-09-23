import re
from langdetect import detect, LangDetectException

def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)      # remover links
    text = re.sub(r"@\w+", "", text)          # remover menções
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"