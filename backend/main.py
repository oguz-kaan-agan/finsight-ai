from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import uuid

from models import (
    NewsItem, AnalyzedNewsItem, AIAnalysisResult, MarketDataResponse, AnalyzeRequest,
    AnalyzeResponse, RSIStatus, OHLCVCandle,
    LoginRequest, LoginResponse,
    RSSSourceCreate, RSSSourceUpdate, RSSSourceResponse,
    ManualNewsCreate, ManualNewsUpdate, ManualNewsResponse,
    SiteSettingsUpdate, DashboardStats,
)
from services.news_service import get_latest_news
from services.ai_service import analyze_news_sentiment
from services.market_data_service import get_market_data, get_chart_data
from services.indicators import get_rsi_status
from auth import login, verify_token, logout
import database as db

# Uygulama başlangıcında DB'yi başlat
db.init_db()

app = FastAPI(title="FinSight AI - Financial News Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════
# PUBLIC API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {"message": "FinSight AI Financial News Analysis API is running", "version": "2.0"}


@app.get("/api/news", response_model=List[AnalyzedNewsItem])
async def fetch_and_analyze_news():
    loop = asyncio.get_event_loop()
    
    # Ayarlardan max_news değerini çek
    settings = await loop.run_in_executor(None, db.get_site_settings)
    max_news = int(settings.get("max_news", "20"))
    
    # Önbellekten haberleri al
    cached_news = await loop.run_in_executor(None, db.get_cached_news, max_news)
    
    analyzed_items = []
    from datetime import datetime
    for item in cached_news:
        try:
            pub_date = datetime.fromisoformat(item["published_at"])
        except ValueError:
            pub_date = datetime.utcnow()
            
        analyzed_items.append(AnalyzedNewsItem(
            news=NewsItem(
                id=item["id"],
                title=item["title"],
                content=item["content"],
                source=item["source"],
                published_at=pub_date,
                url=item.get("url")
            ),
            analysis=AIAnalysisResult(
                sentiment=item["sentiment"] or "Neutral",
                affected_sectors=item["affected_sectors"] or [],
                affected_instruments=item["affected_instruments"] or [],
                impact_summary=item["impact_summary"] or ""
            ) if item["sentiment"] else None
        ))
        
    # Eğer önbellekte hiç haber yoksa (Örn: DB sıfırlanmış veya ilk kez kurulmuşsa)
    # Kullanıcıyı boş bırakmamak için eski usul anlık çek
    if not analyzed_items:
        print("No cached news found, triggering instant fallback scrape...")
        news_items = await loop.run_in_executor(None, get_latest_news)
        for item in news_items:
            analyzed_items.append(AnalyzedNewsItem(
                news=item,
                analysis=None
            ))
            
    return analyzed_items


async def analyze_and_cache_single_news(news_id: str, title: str, content: str, source: str, published_at: str, url: str):
    """Tekil bir manuel haberi analiz edip veritabanına önbellekler."""
    try:
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(None, analyze_news_sentiment, title, content)
        
        sentiment = "Neutral"
        affected_sectors = []
        affected_instruments = []
        impact_summary = ""
        
        if analysis:
            sentiment = getattr(analysis, "sentiment", "Neutral")
            affected_sectors = getattr(analysis, "affected_sectors", [])
            affected_instruments = getattr(analysis, "affected_instruments", [])
            impact_summary = getattr(analysis, "impact_summary", "")
            
        await loop.run_in_executor(
            None,
            db.save_analyzed_news,
            news_id,
            title,
            content,
            source,
            published_at,
            url or "",
            sentiment,
            affected_sectors,
            affected_instruments,
            impact_summary
        )
        print(f"Successfully cached newly added manual news: {title}")
    except Exception as e:
        print(f"Error in analyze_and_cache_single_news: {e}")


async def news_fetcher_loop():
    """Arka planda haberleri periyodik olarak çeken ve analiz eden döngü."""
    # Başlangıçta 5 saniye bekle (Uygulamanın tam ayağa kalkması için)
    await asyncio.sleep(5)
    while True:
        try:
            print("Background news fetcher starting...")
            loop = asyncio.get_event_loop()
            
            # 1. Eski haberleri temizle (7 günden eskiler)
            cleaned = await loop.run_in_executor(None, db.cleanup_old_news, 7)
            if cleaned > 0:
                print(f"Cleaned up {cleaned} old cached news items.")
                
            # 2. Güncel haberleri çek (RSS + manual)
            news_items = await loop.run_in_executor(None, get_latest_news)
            
            # 3. Zaten önbelleklenmiş olan haberleri belirle
            cached_news_list = await loop.run_in_executor(None, db.get_cached_news, 100)
            cached_titles = {n["title"].lower().strip() for n in cached_news_list}
            
            # 4. Sadece yeni olan haberleri ayıkla ve analiz et
            new_articles_count = 0
            for item in news_items:
                title_clean = item.title.lower().strip()
                if title_clean not in cached_titles:
                    print(f"Analyzing new article with Gemini: {item.title}")
                    # Gemini analizi yap
                    analysis = await loop.run_in_executor(
                        None, 
                        analyze_news_sentiment, 
                        item.title, 
                        item.content
                    )
                    
                    # Veritabanına kaydet
                    sentiment = "Neutral"
                    affected_sectors = []
                    affected_instruments = []
                    impact_summary = ""
                    
                    if analysis:
                        sentiment = getattr(analysis, "sentiment", "Neutral")
                        affected_sectors = getattr(analysis, "affected_sectors", [])
                        affected_instruments = getattr(analysis, "affected_instruments", [])
                        impact_summary = getattr(analysis, "impact_summary", "")
                        
                    await loop.run_in_executor(
                        None,
                        db.save_analyzed_news,
                        item.id,
                        item.title,
                        item.content,
                        item.source,
                        item.published_at.isoformat(),
                        item.url or "",
                        sentiment,
                        affected_sectors,
                        affected_instruments,
                        impact_summary
                    )
                    new_articles_count += 1
            print(f"Background news fetcher loop completed iteration. Analyzed {new_articles_count} new articles.")
        except Exception as e:
            print(f"Error in news fetcher loop: {e}")
        
        # 10 dakika bekle (600 saniye)
        await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    # Arka plan görevini başlat
    asyncio.create_task(news_fetcher_loop())



@app.get("/api/market-data/{symbol}", response_model=MarketDataResponse)
async def get_symbol_data(symbol: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_market_data, symbol)
    return result


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_custom_news(request: AnalyzeRequest):
    loop = asyncio.get_event_loop()
    analysis = await loop.run_in_executor(None, analyze_news_sentiment, request.title, request.content)

    rsi_data = []
    if analysis and analysis.affected_instruments:
        for symbol in analysis.affected_instruments:
            status = await loop.run_in_executor(None, get_rsi_status, symbol)
            rsi_data.append(RSIStatus(symbol=symbol, rsi_status=status))

    return AnalyzeResponse(analysis=analysis, rsi_data=rsi_data)


@app.get("/api/chart-data/{symbol}", response_model=List[OHLCVCandle])
async def get_chart(symbol: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_chart_data, symbol)
    return result


@app.get("/api/settings")
async def get_public_settings():
    """Herkese açık site ayarları (başlık, açıklama)."""
    settings = db.get_site_settings()
    return {
        "site_title": settings.get("site_title", "FinSight AI"),
        "site_description": settings.get("site_description", ""),
    }


# ══════════════════════════════════════════════════════════════════════
# ADMIN API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

# ── Auth ──────────────────────────────────────────────────────────────

@app.post("/api/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    token = login(request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Geçersiz şifre")
    return LoginResponse(token=token, message="Giriş başarılı")


@app.post("/api/admin/logout")
async def admin_logout(authenticated: bool = Depends(verify_token)):
    return {"message": "Çıkış başarılı"}


# ── Dashboard Stats ──────────────────────────────────────────────────

@app.get("/api/admin/stats", response_model=DashboardStats)
async def admin_stats(authenticated: bool = Depends(verify_token)):
    rss_all = db.get_rss_sources()
    rss_active = db.get_rss_sources(active_only=True)
    news_all = db.get_manual_news()
    news_active = db.get_manual_news(active_only=True)
    return DashboardStats(
        total_rss_sources=len(rss_all),
        active_rss_sources=len(rss_active),
        total_manual_news=len(news_all),
        active_manual_news=len(news_active),
    )


# ── RSS Sources CRUD ─────────────────────────────────────────────────

@app.get("/api/admin/rss-sources", response_model=List[RSSSourceResponse])
async def list_rss_sources(authenticated: bool = Depends(verify_token)):
    return db.get_rss_sources()


@app.post("/api/admin/rss-sources", response_model=RSSSourceResponse, status_code=201)
async def create_rss_source(source: RSSSourceCreate, authenticated: bool = Depends(verify_token)):
    try:
        return db.add_rss_source(source.name, source.url, source.max_entries)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kaynak eklenemedi: {str(e)}")


@app.put("/api/admin/rss-sources/{source_id}", response_model=RSSSourceResponse)
async def update_rss_source(source_id: int, source: RSSSourceUpdate, authenticated: bool = Depends(verify_token)):
    result = db.update_rss_source(source_id, source.name, source.url, source.max_entries, source.is_active)
    if not result:
        raise HTTPException(status_code=404, detail="Kaynak bulunamadı")
    return result


@app.delete("/api/admin/rss-sources/{source_id}")
async def delete_rss_source(source_id: int, authenticated: bool = Depends(verify_token)):
    if not db.delete_rss_source(source_id):
        raise HTTPException(status_code=404, detail="Kaynak bulunamadı")
    return {"message": "Kaynak silindi"}


# ── Manual News CRUD ─────────────────────────────────────────────────

@app.get("/api/admin/news", response_model=List[ManualNewsResponse])
async def list_manual_news(authenticated: bool = Depends(verify_token)):
    return db.get_manual_news()


@app.post("/api/admin/news", response_model=ManualNewsResponse, status_code=201)
async def create_manual_news(news: ManualNewsCreate, authenticated: bool = Depends(verify_token)):
    news_id = str(uuid.uuid4())
    result = db.add_manual_news(news_id, news.title, news.content, news.source, news.url)
    
    # Arka planda anında analiz edip önbelleğe ekle
    asyncio.create_task(analyze_and_cache_single_news(
        news_id, news.title, news.content, news.source, result["published_at"], news.url
    ))
    return result


@app.put("/api/admin/news/{news_id}", response_model=ManualNewsResponse)
async def update_manual_news(news_id: str, news: ManualNewsUpdate, authenticated: bool = Depends(verify_token)):
    result = db.update_manual_news(news_id, news.title, news.content, news.source, news.url, news.is_active)
    if not result:
        raise HTTPException(status_code=404, detail="Haber bulunamadı")
    
    # Aktif ise önbelleğe ekle/güncelle, pasif ise önbellekten sil
    if news.is_active:
        asyncio.create_task(analyze_and_cache_single_news(
            news_id, news.title, news.content, news.source, result["published_at"], news.url
        ))
    else:
        db.delete_analyzed_news_by_id(news_id)
        
    return result


@app.delete("/api/admin/news/{news_id}")
async def delete_manual_news(news_id: str, authenticated: bool = Depends(verify_token)):
    if not db.delete_manual_news(news_id):
        raise HTTPException(status_code=404, detail="Haber bulunamadı")
    # Önbellekten de sil
    db.delete_analyzed_news_by_id(news_id)
    return {"message": "Haber silindi"}


# ── Site Settings ─────────────────────────────────────────────────────

@app.get("/api/admin/settings")
async def get_settings(authenticated: bool = Depends(verify_token)):
    return db.get_site_settings()


@app.put("/api/admin/settings")
async def update_settings(settings: SiteSettingsUpdate, authenticated: bool = Depends(verify_token)):
    update_dict = {k: v for k, v in settings.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="En az bir ayar belirtilmelidir")
    return db.update_site_settings(update_dict)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
