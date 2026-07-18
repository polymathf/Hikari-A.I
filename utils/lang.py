import json

with open("locales/languages.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

def t(key: str, lang: str = "eng", **kwargs) -> str:
    text = translations.get(key, {}).get(lang, "")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            print(f"Missing key in translation formatting: {e}")
    return text
