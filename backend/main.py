from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import uuid

from models import (
    NewsItem, AnalyzedNewsItem, MarketDataResponse, AnalyzeRequest,
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

    # Haberleri çek (RSS + manual)
    news_items = await loop.run_in_executor(None, get_latest_news)
    # Haberleri paralel olarak analiz et
    tasks = []
    for item in news_items:
        task = loop.run_in_executor(None, analyze_news_sentiment, item.title, item.content)
        tasks.append(task)
        
    analyses = await asyncio.gather(*tasks)
    
    analyzed_items = []
    for item, analysis in zip(news_items, analyses):
        analyzed_items.append(AnalyzedNewsItem(
            news=item,
            analysis=analysis
        ))

    return analyzed_items


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
    return db.add_manual_news(news_id, news.title, news.content, news.source, news.url)


@app.put("/api/admin/news/{news_id}", response_model=ManualNewsResponse)
async def update_manual_news(news_id: str, news: ManualNewsUpdate, authenticated: bool = Depends(verify_token)):
    result = db.update_manual_news(news_id, news.title, news.content, news.source, news.url, news.is_active)
    if not result:
        raise HTTPException(status_code=404, detail="Haber bulunamadı")
    return result


@app.delete("/api/admin/news/{news_id}")
async def delete_manual_news(news_id: str, authenticated: bool = Depends(verify_token)):
    if not db.delete_manual_news(news_id):
        raise HTTPException(status_code=404, detail="Haber bulunamadı")
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
