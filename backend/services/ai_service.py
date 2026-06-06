import os
import json
import time
from google import genai
from google.genai import types
from models import AIAnalysisResult
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

# Sadece stabil / güncel modeller
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

import hashlib

_analysis_cache = {}

def analyze_news_sentiment(title: str, content: str) -> AIAnalysisResult | None:
    # Başlık ve içeriğe göre hash oluşturup önbellekte arıyoruz
    cache_key = hashlib.md5(f"{title}_{content}".encode()).hexdigest()
    if cache_key in _analysis_cache:
        return _analysis_cache[cache_key]

    if not client:
        print("Warning: GEMINI_API_KEY not found. Returning mock analysis.")
        return _get_mock_analysis(title)

    prompt = f"""Aşağıdaki finansal haberi analiz et ve kesinlikle JSON formatında yanıt dön.
Serbest metin yazma, sadece JSON objesi döndür.

Haber Başlığı: {title}
Haber İçeriği: {content[:800]}

İstenen JSON şeması:
{{
    "sentiment": "Positive" veya "Negative" veya "Neutral",
    "affected_sectors": ["Teknoloji", "Havacılık", "Enerji" gibi sektör listesi],
    "affected_instruments": ["THYAO", "PGSUS", "AAPL", "BTC" gibi ticker listesi],
    "impact_summary": "Haberin enstrümanlar üzerindeki etkisinin kısa mantıksal açıklaması."
}}

KESİN KURALLAR - Uymayan semboller listeye EKLEME:
1. BIST hisseleri: THYAO, GARAN, AKBNK, ISCTR, TUPRS, SASA, TAVHL, FROTO, TOASO, ASELS, TCELL, ARCLK, BIMAS, KCHOL, EREGL, SISE, SAHOL, YKBNK, HALKB, VAKBN, TTKOM, PETKM, DOAS, MGROS, VESTL, EKGYO, KOZAL, ULKER, ENKAI, LOGO gibi (sadece ticker, ".IS" EKLEME)
2. Kripto: BTC, ETH, BNB, SOL, XRP, ADA, AVAX, DOT, DOGE, LINK, SUI, TON gibi
3. ABD hisseleri: AAPL, TSLA, MSFT, NVDA, AMZN, GOOGL, META, AMD, INTC gibi
4. Emtia: ALTIN (altın), PETROL (ham petrol), GUMUS (gümüş), BRENT (Brent petrol), DOGALGAZ (doğalgaz)
5. Endeksler: XU100, BIST100, SPX, NASDAQ, DJI gibi
6. Döviz: USDTRY, EURTRY, EURUSD, DOLAR, EURO gibi
7. Sadece haber içeriğinde açıkça geçen veya doğrudan etkilenen enstrümanları ekle
8. Eğer sembol gerçekten hangi borsada işlem gördüğünden emin değilsen affected_instruments listesini BOŞ bırak"""

    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            result_dict = json.loads(response.text)
            result = AIAnalysisResult(**result_dict)
            _analysis_cache[cache_key] = result
            return result

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"Model {model_name} kota aşıldı, sonraki model deneniyor...")
                time.sleep(1)
                continue
            elif "404" in error_str or "NOT_FOUND" in error_str:
                print(f"Model {model_name} bulunamadı, sonraki deneniyor...")
                continue
            else:
                print(f"Model {model_name} hatası: {e}")
                continue

    # Tüm modeller başarısız - mock analiz döndür
    print("Tüm Gemini modelleri başarısız. Mock analiz kullanılıyor.")
    result = _get_mock_analysis(title)
    _analysis_cache[cache_key] = result
    return result


def _get_mock_analysis(title: str) -> AIAnalysisResult:
    """
    API kullanılamadığında içerik bazlı basit kural tabanlı analiz.
    """
    title_lower = title.lower()

    # Sentiment tahmini
    positive_words = ["yükseldi", "artış", "büyüme", "kazanç", "rekor", "güçlendi", "olumlu", "başarı", "rally", "surge"]
    negative_words = ["düştü", "geriledi", "kayıp", "zarar", "kriz", "risk", "endişe", "düşüş", "crash", "fall"]

    sentiment = "Neutral"
    for word in positive_words:
        if word in title_lower:
            sentiment = "Positive"
            break
    for word in negative_words:
        if word in title_lower:
            sentiment = "Negative"
            break

    # Sektör ve enstrüman tahmini
    sector_instrument_map = {
        "havacılık": (["Havacılık"], ["THYAO", "PGSUS"]),
        "thy": (["Havacılık"], ["THYAO"]),
        "thyao": (["Havacılık"], ["THYAO"]),
        "pegasus": (["Havacılık"], ["PGSUS"]),
        "bankacılık": (["Bankacılık", "Finans"], ["GARAN", "AKBNK", "ISCTR"]),
        "garanti": (["Bankacılık"], ["GARAN"]),
        "akbank": (["Bankacılık"], ["AKBNK"]),
        "iş bankası": (["Bankacılık"], ["ISCTR"]),
        "faiz": (["Bankacılık", "Finans"], ["GARAN", "AKBNK", "YKBNK"]),
        "bitcoin": (["Kripto"], ["BTC"]),
        "btc": (["Kripto"], ["BTC"]),
        "ethereum": (["Kripto"], ["ETH"]),
        "kripto": (["Kripto"], ["BTC", "ETH"]),
        "enerji": (["Enerji"], ["PETKM", "TUPRS"]),
        "petrol": (["Enerji", "Emtia"], ["PETROL", "TUPRS"]),
        "doğalgaz": (["Enerji", "Emtia"], ["DOGALGAZ"]),
        "rafineri": (["Enerji"], ["TUPRS"]),
        "tüpraş": (["Enerji"], ["TUPRS"]),
        "teknoloji": (["Teknoloji"], ["ASELS", "LOGO"]),
        "apple": (["Teknoloji"], ["AAPL"]),
        "aapl": (["Teknoloji"], ["AAPL"]),
        "nvidia": (["Teknoloji"], ["NVDA"]),
        "microsoft": (["Teknoloji"], ["MSFT"]),
        "tesla": (["Otomotiv", "Teknoloji"], ["TSLA"]),
        "altın": (["Emtia"], ["ALTIN"]),
        "gold": (["Emtia"], ["ALTIN"]),
        "gümüş": (["Emtia"], ["GUMUS"]),
        "dolar": (["Döviz", "Makroekonomi"], ["USDTRY"]),
        "euro": (["Döviz"], ["EURTRY"]),
        "kur": (["Döviz", "Makroekonomi"], ["USDTRY", "EURTRY"]),
        "enflasyon": (["Makroekonomi", "Finans"], []),
        "merkez bankası": (["Makroekonomi", "Bankacılık"], ["GARAN", "AKBNK"]),
        "tcmb": (["Makroekonomi", "Bankacılık"], []),
        "bist": (["Borsa"], ["XU100"]),
        "borsa": (["Borsa"], ["XU100"]),
        "otomotiv": (["Otomotiv"], ["FROTO", "TOASO"]),
        "ford": (["Otomotiv"], ["FROTO"]),
        "tofaş": (["Otomotiv"], ["TOASO"]),
        "savunma": (["Savunma"], ["ASELS"]),
        "aselsan": (["Savunma"], ["ASELS"]),
        "perakende": (["Perakende"], ["BIMAS", "MGROS"]),
        "migros": (["Perakende"], ["MGROS"]),
    }

    sectors = []
    instruments = []

    for keyword, (sec, inst) in sector_instrument_map.items():
        if keyword in title_lower:
            sectors.extend(sec)
            instruments.extend(inst)

    # Tekrarları kaldır
    sectors = list(dict.fromkeys(sectors))
    instruments = list(dict.fromkeys(instruments))

    if not sectors:
        sectors = ["Genel Piyasa"]

    impact = f"Bu haber {', '.join(sectors)} sektörünü etkileyebilir. "
    if instruments:
        impact += f"{', '.join(instruments)} hisselerinde hareket bekleniyor."
    else:
        impact += "Genel piyasa endeksleri izlenmelidir."

    return AIAnalysisResult(
        sentiment=sentiment,
        affected_sectors=sectors,
        affected_instruments=instruments,
        impact_summary=impact
    )
