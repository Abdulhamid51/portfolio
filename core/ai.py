"""Gemini orqali matnni imlo va format jihatidan tozalash.

Tashqi kutubxona ishlatilmaydi — Google Generative Language REST API'siga
oddiy HTTP so'rov yuboriladi. Kalit va model `.env` dan olinadi.
"""
import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

from .richtext import clean_html

logger = logging.getLogger("oldfox")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

MAX_INPUT_CHARS = 20000

SYSTEM_PROMPT = """Sen o'zbek tilidagi matnlarni tahrirlaydigan muharrirsan.
Senga HTML ko'rinishidagi maqola matni beriladi. Vazifang:

1. Imloviy va tinish belgilaridagi xatolarni tuzat (o'zbek lotin yozuvi:
   o', g', sh, ch harflari to'g'ri yozilsin).
2. Gaplarni tabiiy va ravon qil, lekin ma'noni va muallif ohangini saqla.
3. Matnni to'g'ri formatla: mantiqiy bandlarga (<p>) ajrat, kerak bo'lsa
   bo'limlarga sarlavha (<h2>, <h3>) qo'y, sanab o'tilgan narsalarni
   ro'yxatga (<ul>/<ol> va <li>) aylantir, iqtiboslarni <blockquote> ga ol.
4. Kodga o'xshash qismlarni <pre> yoki <code> ichida qoldir.

Qat'iy qoidalar:
- Faqat HTML qaytar. Hech qanday izoh, kirish so'zi yoki ```html belgisi yo'q.
- Yangi ma'lumot, fakt, raqam yoki havola o'ylab topma.
- Matnni boshqa tilga tarjima qilma.
- Rasm (<img>) va havolalarni (<a href>) borligicha saqla.
- Faqat quyidagi teglardan foydalan: p, h2, h3, h4, strong, em, u, s, ul, ol,
  li, blockquote, pre, code, a, img, br, hr, table, thead, tbody, tr, th, td.
"""

USER_TEMPLATE = "Quyidagi matnni tahrirlab, tozalangan HTML holida qaytar:\n\n{html}"


class AssistError(Exception):
    """Foydalanuvchiga ko'rsatiladigan xato."""


def is_enabled():
    return bool(settings.GEMINI_API_KEY)


def _strip_fences(text):
    """Model ```html ... ``` ichida qaytarsa, belgilarni olib tashlaymiz."""
    text = text.strip()
    match = re.match(r"^```[a-zA-Z]*\s*\n(.*)\n?```$", text, re.DOTALL)
    return match.group(1).strip() if match else text


def _ensure_blocks(html):
    """Model oddiy matn qaytarsa, uni bandlarga bo'lamiz."""
    if re.search(r"<(p|h2|h3|h4|ul|ol|blockquote|pre|table)\b", html, re.I):
        return html
    parts = [p.strip() for p in re.split(r"\n{2,}", html) if p.strip()]
    return "".join(f"<p>{p}</p>" for p in parts)


def _call_gemini(payload):
    url = API_URL.format(model=settings.GEMINI_MODEL)
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.GEMINI_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.GEMINI_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")[:400]
        logger.warning("Gemini xatosi %s: %s", exc.code, detail)
        if exc.code in (401, 403):
            raise AssistError("API kalit noto'g'ri yoki ruxsat yo'q.") from exc
        if exc.code == 404:
            raise AssistError(
                f"“{settings.GEMINI_MODEL}” modeli topilmadi — .env dagi nomni tekshiring."
            ) from exc
        if exc.code == 429:
            raise AssistError("So'rovlar chegarasi tugadi. Birozdan so'ng urinib ko'ring.") from exc
        raise AssistError(f"Gemini xatosi ({exc.code}).") from exc
    except urllib.error.URLError as exc:
        logger.warning("Gemini ga ulanib bo'lmadi: %s", exc)
        raise AssistError("Gemini xizmatiga ulanib bo'lmadi.") from exc
    except TimeoutError as exc:
        raise AssistError("Gemini javob bermadi (vaqt tugadi).") from exc


def _extract_text(data):
    feedback = data.get("promptFeedback") or {}
    if feedback.get("blockReason"):
        raise AssistError("Matn xavfsizlik filtridan o'tmadi.")

    candidates = data.get("candidates") or []
    if not candidates:
        raise AssistError("Model javob qaytarmadi.")

    candidate = candidates[0]
    parts = (candidate.get("content") or {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        reason = candidate.get("finishReason", "")
        if reason == "MAX_TOKENS":
            raise AssistError("Matn juda uzun — qisqaroq bo'lak bilan urinib ko'ring.")
        raise AssistError("Model bo'sh javob qaytardi.")
    return text


def tidy_html(html):
    """HTML matnni Gemini orqali tozalab, xavfsiz HTML qaytaradi."""
    if not is_enabled():
        raise AssistError("Gemini kaliti sozlanmagan (.env dagi GEMINI_API_KEY).")

    source = (html or "").strip()
    if not source:
        raise AssistError("Avval matn yozing.")
    if len(source) > MAX_INPUT_CHARS:
        raise AssistError(
            f"Matn juda katta ({len(source)} belgi). "
            f"{MAX_INPUT_CHARS} belgigacha bo'lgan qismini yuboring."
        )

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": USER_TEMPLATE.format(html=source)}]}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain",
        },
    }

    text = _extract_text(_call_gemini(payload))
    # Model javobi ham ishonchsiz manba — saqlashdan oldin tozalanadi
    cleaned = clean_html(_ensure_blocks(_strip_fences(text)))
    if not cleaned:
        raise AssistError("Tozalangan matn bo'sh chiqdi.")
    return cleaned
