from datetime import datetime

HI = {"ai":"एआई", "automation":"ऑटोमेशन", "social":"सोशल", "media":"मीडिया", "helps":"मदद करता है", "creators":"क्रिएटर्स", "save":"बचाने", "time":"समय", "grow":"बढ़ने", "business":"बिजनेस", "content":"कंटेंट", "post":"पोस्ट", "marketing":"मार्केटिंग", "tools":"टूल्स", "learn":"सीखें", "share":"शेयर करें", "comment":"कमेंट करें", "follow":"फॉलो करें", "today":"आज"}
MR = {"ai":"एआय", "automation":"ऑटोमेशन", "social":"सोशल", "media":"मीडिया", "helps":"मदत करते", "creators":"क्रिएटर्स", "save":"वाचवण्यासाठी", "time":"वेळ", "grow":"वाढण्यासाठी", "business":"बिझनेस", "content":"कंटेंट", "post":"पोस्ट", "marketing":"मार्केटिंग", "tools":"टूल्स", "learn":"शिका", "share":"शेअर करा", "comment":"कमेंट करा", "follow":"फॉलो करा", "today":"आज"}
ES = {"ai":"IA", "automation":"automatización", "social":"social", "media":"medios", "helps":"ayuda", "creators":"creadores", "save":"ahorrar", "time":"tiempo", "grow":"crecer", "business":"negocio", "content":"contenido", "post":"publicación", "marketing":"marketing", "tools":"herramientas", "learn":"aprender", "share":"compartir", "comment":"comentar", "follow":"seguir", "today":"hoy"}

def translate_caption(text, target_language="Hindi"):
    lang = target_language.lower()
    dictionary = HI if lang in ["hindi", "hi"] else MR if lang in ["marathi", "mr"] else ES if lang in ["spanish", "es"] else HI
    out = []
    for word in str(text).split():
        if word.startswith("#") or word.startswith("@"):
            out.append(word)
        else:
            key = ''.join(ch for ch in word.lower() if ch.isalnum())
            out.append(dictionary.get(key, word))
    translated = " ".join(out)
    return {"original_text": text, "target_language": target_language, "translated_text": translated, "translation_type": "offline_dictionary_fallback", "translated_at": datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    print(translate_caption("AI automation helps creators save time #AI", "Hindi"))
