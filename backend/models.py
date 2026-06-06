from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NewsItem(BaseModel):
    id: str
    title: str
    content: str
    source: str
    published_at: datetime
    url: Optional[str] = None

class AIAnalysisResult(BaseModel):
    sentiment: str  # "Positive", "Negative", "Neutral"
    affected_sectors: List[str]
    affected_instruments: List[str]
    impact_summary: str

class AnalyzedNewsItem(BaseModel):
    news: NewsItem
    analysis: Optional[AIAnalysisResult] = None

class RSIData(BaseModel):
    period: str  # "4H" or "Daily"
    rsi_value: Optional[float]
    status: str  # "Ucuz", "Nötr", "Pahalı", or "Veri Yok"

class MarketDataResponse(BaseModel):
    symbol: str
    current_price: Optional[float]
    ltf_rsi: RSIData
    htf_rsi: RSIData

class AnalyzeRequest(BaseModel):
    title: str
    content: str

class RSIStatus(BaseModel):
    symbol: str
    rsi_status: str

class AnalyzeResponse(BaseModel):
    analysis: Optional[AIAnalysisResult]
    rsi_data: List[RSIStatus]

class OHLCVCandle(BaseModel):
    time: str  # "YYYY-MM-DD"
    open: float
    high: float
    low: float
    close: float
    volume: int


# ── Admin Modelleri ───────────────────────────────────────────────────

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

class RSSSourceCreate(BaseModel):
    name: str
    url: str
    max_entries: int = 10

class RSSSourceUpdate(BaseModel):
    name: str
    url: str
    max_entries: int = 10
    is_active: bool = True

class RSSSourceResponse(BaseModel):
    id: int
    name: str
    url: str
    max_entries: int
    is_active: int
    created_at: str

class ManualNewsCreate(BaseModel):
    title: str
    content: str
    source: str = "Admin"
    url: str = ""

class ManualNewsUpdate(BaseModel):
    title: str
    content: str
    source: str = "Admin"
    url: str = ""
    is_active: bool = True

class ManualNewsResponse(BaseModel):
    id: str
    title: str
    content: str
    source: str
    published_at: str
    url: Optional[str] = None
    is_active: int
    created_at: str

class SiteSettingsUpdate(BaseModel):
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    max_news: Optional[str] = None

class DashboardStats(BaseModel):
    total_rss_sources: int
    active_rss_sources: int
    total_manual_news: int
    active_manual_news: int
