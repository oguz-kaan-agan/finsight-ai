import uuid
from datetime import datetime
from typing import List
import feedparser
import re
from models import NewsItem
import database as db

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    # Birden fazla boşluk/newline'ı tek boşluğa çevir
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()


def _parse_published_date(entry) -> datetime:
    """RSS entry'den yayın tarihini çıkarmaya çalışır."""
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            from time import mktime
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            from time import mktime
            return datetime.fromtimestamp(mktime(entry.updated_parsed))
    except Exception:
        pass
    return datetime.utcnow()


import urllib.request

def fetch_feed_with_timeout(url: str, timeout: float = 1.5) -> bytes | None:
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except Exception as e:
        print(f"RSS download hatası ({url}): {e}")
        return None

def get_latest_news() -> List[NewsItem]:
    news_items = []
    seen_titles = set()  # Aynı haberin tekrarını engelle

    # ── DB'den aktif RSS kaynaklarını çek ──
    rss_sources = db.get_rss_sources(active_only=True)

    for source in rss_sources:
        source_name = source["name"]
        rss_url = source["url"]
        max_entries = source["max_entries"]

        try:
            feed_data = fetch_feed_with_timeout(rss_url, timeout=1.5)
            if not feed_data:
                continue
            feed = feedparser.parse(feed_data)
            if not feed.entries:
                continue

            for entry in feed.entries[:max_entries]:
                title = entry.get('title', '').strip()

                # Başlık tekrarını engelle
                if not title or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())

                content = entry.get('summary', '')
                if not content:
                    content = entry.get('description', '')

                content = clean_html(content)

                if not content:
                    content = title

                published_at = _parse_published_date(entry)

                news_items.append(
                    NewsItem(
                        id=str(uuid.uuid4()),
                        title=title,
                        content=content,
                        source=source_name,
                        published_at=published_at,
                        url=entry.get('link', '')
                    )
                )

        except Exception as e:
            print(f"RSS feed hatası ({source_name}): {e}")
            continue

    # ── DB'den aktif manuel haberleri ekle ──
    manual_news = db.get_manual_news(active_only=True)
    for mn in manual_news:
        title = mn["title"].strip()
        if title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        news_items.append(
            NewsItem(
                id=mn["id"],
                title=title,
                content=mn["content"],
                source=mn["source"],
                published_at=datetime.fromisoformat(mn["published_at"]),
                url=mn.get("url", ""),
            )
        )

    # Tarihe göre sırala (en yeni en üstte)
    news_items.sort(key=lambda x: x.published_at, reverse=True)

    # DB'den max_news ayarını oku
    settings = db.get_site_settings()
    max_news = int(settings.get("max_news", "20"))

    # Hiç haber gelemediyse fallback demo haberler
    if not news_items:
        print("Tüm RSS kaynakları başarısız. Fallback haberler kullanılıyor.")
        news_items = get_fallback_news()

    return news_items[:max_news]

def get_fallback_news() -> List[NewsItem]:
    """RSS başarısız olduğunda demo haberler döndürür."""
    demo_news = [
        {
            "title": "Türkiye Merkez Bankası faiz kararını açıkladı",
            "content": "TCMB Para Politikası Kurulu toplantısında politika faizini sabit tutma kararı aldı. Enflasyonla mücadelede kararlı duruş sürdürülüyor. Bankacılık sektörü ve BIST endeksi bu karara tepki gösterdi.",
            "source": "Demo Haber",
            "url": "#"
        },
        {
            "title": "THY yeni uçuş güzergahları açıkladı, hisseleri yükseldi",
            "content": "Türk Hava Yolları, 2024 yaz sezonu için 15 yeni destinasyon ekleyeceğini duyurdu. Şirket hisseleri bu haberin ardından BIST'te %3 değer kazandı. Havacılık sektörüne olan ilgi artıyor.",
            "source": "Demo Haber",
            "url": "#"
        },
        {
            "title": "Enerji fiyatları rekor kırdı, petrol 90 doların üzerine çıktı",
            "content": "Ham petrol fiyatları küresel arz endişeleriyle 90 doların üzerine çıktı. OPEC+ üretim kısıtlamalarını sürdürme kararı aldı. Enerji şirketlerinin hisse senetleri güçlü seyrediyor.",
            "source": "Demo Haber",
            "url": "#"
        },
        {
            "title": "Bitcoin 70.000 dolara yaklaşıyor, kripto piyasaları hareketli",
            "content": "Bitcoin spot ETF onaylarının ardından kripto para piyasaları hareketlendi. BTC 70.000 dolar sınırına yaklaşırken Ethereum da güçlü performans sergiledi. Kripto yatırımcıları yeni zirveleri bekliyor.",
            "source": "Demo Haber",
            "url": "#"
        },
        {
            "title": "Teknoloji devleri yapay zeka yatırımlarını artırıyor",
            "content": "Apple, Microsoft ve NVIDIA yapay zeka altyapısına milyar dolarlık yatırım yapacaklarını açıkladı. Teknoloji sektörü hisseleri bu açıklamaların ardından yükseliş kaydetti. BIST teknoloji endeksi de olumlu etkilendi.",
            "source": "Demo Haber",
            "url": "#"
        },
    ]

    return [
        NewsItem(
            id=str(uuid.uuid4()),
            title=item["title"],
            content=item["content"],
            source=item["source"],
            published_at=datetime.utcnow(),
            url=item["url"]
        )
        for item in demo_news
    ]
