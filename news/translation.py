from deep_translator import GoogleTranslator

EU_LANGS = [
    "en", "de", "fr", "it", "es", "pl", "hu", "nl", "pt", "cs", "sk", "fi", "sv", "da", "no",
    "ga", "bg", "ro", "el", "lt", "lv", "et", "hr", "sr", "bs", "sl", "sq", "mk", "cy", "mt", "ru", "uk"
]

def translate_keywords(keyword: str):
    translated = {}
    for lang in EU_LANGS:
        try:
            translated[lang] = GoogleTranslator(source='auto', target=lang).translate(keyword)
        except Exception as e:
            translated[lang] = keyword
    return translated
