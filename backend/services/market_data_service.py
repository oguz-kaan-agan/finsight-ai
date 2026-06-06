import yfinance as yf
import pandas as pd
from typing import Optional, List
from models import MarketDataResponse, RSIData, OHLCVCandle

# Türk hisse senetleri için BIST suffix ekleme — genişletilmiş liste
TURKISH_STOCKS = {
    # BIST-30
    "THYAO", "PGSUS", "AKBNK", "GARAN", "ISCTR", "SISE", "EREGL", "BIMAS",
    "KCHOL", "FROTO", "TOASO", "ASELS", "TCELL", "ARCLK", "EKGYO", "KOZAL",
    "SAHOL", "YKBNK", "HALKB", "VAKBN", "TTKOM", "ENKAI", "PETKM", "ULKER",
    "MAVI", "LOGO", "NETAS", "TURSG", "KLNMA", "SKBNK",
    # BIST-50 ve BIST-100 ek hisseler
    "TUPRS", "SASA", "TAVHL", "DOHOL", "KOZAA", "KONTR", "VESTL", "MGROS",
    "OTKAR", "KORDS", "AEFES", "TTRAK", "PRKME", "ALARK", "CIMSA", "CEMTS",
    "SOKM", "AYGAZ", "ISGYO", "ISMEN", "OYAKC", "BRISA", "TSKB", "TKFEN",
    "GUBRF", "BRSAN", "SUNTK", "AKSEN", "TRGYO", "GENIL", "VESBE", "ALBRK",
    "DOAS", "ANHYT", "GEDZA", "ODAS", "AHGAZ", "AKSA", "ALFAS", "ASUZU",
    "AYDEM", "BAGFS", "BERA", "BIOEN", "BUCIM", "CANTE", "CCOLA", "DEVA",
    "EGEEN", "ENJSA", "EUPWR", "GESAN", "GLYHO", "GWIND", "HEKTS", "IPEKE",
    "ISDMR", "KARSN", "KAYSE", "KERVT", "KLRHO", "KMPUR", "KONTR", "KONYA",
    "KZBGY", "LKMNH", "MAGEN", "MPARK", "NTHOL", "NUGYO", "OBAMS", "PAPIL",
    "PEGYO", "PGSUS", "POLHO", "QUAGR", "RGYAS", "SARKY", "SELEC", "SMRTG",
    "SNGYO", "TATGD", "TKNSA", "TMPOL", "TMSN", "TOASO", "TRGYO", "TRILC",
    "TSPOR", "TUKAS", "TURSG", "ULUUN", "VAKKO", "VERUS", "YATAS", "ZOREN",
    # Bankacılık ek
    "DENIZ", "QNBFB", "ICBCT",
}

CRYPTO_MAP = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "BNB": "BNB-USD",
    "SOL": "SOL-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "AVAX": "AVAX-USD",
    "DOT": "DOT-USD",
    "DOGE": "DOGE-USD",
    "LINK": "LINK-USD",
    "MATIC": "MATIC-USD",
    "SHIB": "SHIB-USD",
    "UNI": "UNI-USD",
    "ATOM": "ATOM-USD",
    "LTC": "LTC-USD",
    "FIL": "FIL-USD",
    "NEAR": "NEAR-USD",
    "APT": "APT-USD",
    "ARB": "ARB-USD",
    "OP": "OP-USD",
    "AAVE": "AAVE-USD",
    "MKR": "MKR-USD",
    "FTM": "FTM-USD",
    "SAND": "SAND-USD",
    "MANA": "MANA-USD",
    "CRO": "CRO-USD",
    "ALGO": "ALGO-USD",
    "ICP": "ICP-USD",
    "VET": "VET-USD",
    "HBAR": "HBAR-USD",
    "TRX": "TRX-USD",
    "ETC": "ETC-USD",
    "XLM": "XLM-USD",
    "SUI": "SUI-USD",
    "TON": "TON-USD",
    "PEPE": "PEPE-USD",
    "RENDER": "RENDER-USD",
}

COMMODITY_MAP = {
    "GC=F": "GC=F",        # Altın futures
    "ALTIN": "GC=F",
    "GOLD": "GC=F",
    "XAU": "GC=F",         # Broker kodu -> yfinance
    "CL=F": "CL=F",        # Ham petrol WTI
    "PETROL": "CL=F",
    "OIL": "CL=F",
    "BRENT": "BZ=F",       # Brent petrol
    "XBR": "BZ=F",
    "SI=F": "SI=F",        # Gümüş futures
    "GUMUS": "SI=F",
    "SILVER": "SI=F",
    "XAG": "SI=F",
    "HG=F": "HG=F",        # Bakır
    "NG=F": "NG=F",        # Doğalgaz
    "NGAS": "NG=F",
    "DOGALGAZ": "NG=F",
    "PL=F": "PL=F",        # Platin
    "PA=F": "PA=F",        # Paladyum
}

FOREX_MAP = {
    "USDTRY": "USDTRY=X",
    "EURTRY": "EURTRY=X",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "GBPTRY": "GBPTRY=X",
    "DOLAR": "USDTRY=X",
    "EURO": "EURTRY=X",
    "DXY": "DX-Y.NYB",     # Dollar Index
}

INDEX_MAP = {
    "XU100": "XU100.IS",
    "BIST100": "XU100.IS",
    "BIST30": "XU030.IS",
    "XU030": "XU030.IS",
    "SPX": "^GSPC",
    "SP500": "^GSPC",
    "NDX": "^IXIC",
    "NASDAQ": "^IXIC",
    "DJI": "^DJI",
    "DOW": "^DJI",
    "DAX": "^GDAXI",
    "FTSE": "^FTSE",
    "NIKKEI": "^N225",
    "VIX": "^VIX",
}


def normalize_symbol(symbol: str) -> str:
    """Sembolü yfinance için uygun formata çevirir."""
    sym = symbol.upper().strip()
    
    # Zaten yfinance formatında ise olduğu gibi bırak
    if ".IS" in sym or "=X" in sym or "=F" in sym or sym.startswith("^"):
        return sym
    
    # Endeks kontrolü
    if sym in INDEX_MAP:
        return INDEX_MAP[sym]
    
    # Kripto kontrolü
    if sym in CRYPTO_MAP:
        return CRYPTO_MAP[sym]
    
    # Emtia kontrolü
    if sym in COMMODITY_MAP:
        return COMMODITY_MAP[sym]

    # Forex kontrolü
    if sym in FOREX_MAP:
        return FOREX_MAP[sym]
    
    # Bilinen Türk hissesi
    if sym in TURKISH_STOCKS:
        return f"{sym}.IS"
    
    # "-USD" suffix'i varsa kripto
    if "-USD" in sym:
        return sym
    
    # Bilinmeyen sembol — ABD hissesi olarak dene
    return sym


def _try_fetch_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Verilen sembol için yfinance'den veri çekmeye çalışır.
    Başarısızsa farklı suffix'ler dener.
    """
    primary = normalize_symbol(symbol)
    
    # Denenecek sembol alternatifleri
    candidates = [primary]
    
    sym_upper = symbol.upper().strip()
    
    # Eğer primary zaten .IS değilse ve pure alfabetik ise, .IS ile de dene
    if ".IS" not in primary and "=" not in primary and "^" not in primary and "-" not in primary:
        candidates.append(f"{sym_upper}.IS")  # Belki Türk hissesi
    
    # Kripto olabilir
    if "-USD" not in primary and len(sym_upper) <= 5 and sym_upper.isalpha():
        candidates.append(f"{sym_upper}-USD")
    
    for candidate in candidates:
        try:
            ticker = yf.Ticker(candidate)
            hist = ticker.history(period=period, interval=interval)
            if hist is not None and not hist.empty and len(hist) >= 5:
                return hist
        except Exception as e:
            print(f"  Sembol denemesi başarısız ({candidate}): {e}")
            continue
    
    return pd.DataFrame()


def calculate_rsi(data: pd.Series, periods: int = 14) -> Optional[float]:
    if len(data) < periods + 1:
        return None
    
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # EMA tabanlı RSI (Wilder's smoothing)
    roll_up = up.ewm(com=periods - 1, adjust=False).mean()
    roll_down = down.ewm(com=periods - 1, adjust=False).mean()
    
    roll_down = roll_down.replace(0, 0.0001)
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    rsi_val = rsi.iloc[-1]
    if pd.isna(rsi_val):
        return None
    return float(rsi_val)


def get_rsi_label(rsi: Optional[float]) -> str:
    if rsi is None:
        return "Veri Yok"
    if rsi < 30:
        return "Ucuz"
    elif rsi > 70:
        return "Pahalı"
    else:
        return "Nötr"


def get_market_data(symbol: str) -> MarketDataResponse:
    yf_symbol = normalize_symbol(symbol)
    
    try:
        # Günlük RSI için 3 aylık veri — smart fetch
        hist_daily = _try_fetch_history(symbol, period="3mo", interval="1d")
        daily_rsi_val = calculate_rsi(hist_daily['Close']) if not hist_daily.empty else None

        # 4H RSI için: yfinance 1h verisini alıp 4H'e resample ediyoruz
        ltf_rsi_val = None
        try:
            hist_1h = _try_fetch_history(symbol, period="60d", interval="1h")
            if not hist_1h.empty and len(hist_1h) >= 10:
                # Index'i timezone-aware yap
                if hist_1h.index.tz is None:
                    hist_1h.index = hist_1h.index.tz_localize('UTC')
                hist_4h = hist_1h['Close'].resample('4h').last().dropna()
                ltf_rsi_val = calculate_rsi(hist_4h)
        except Exception as e:
            print(f"4H RSI hesaplanamadı ({yf_symbol}): {e}")

        current_price = None
        if not hist_daily.empty:
            current_price = float(hist_daily['Close'].iloc[-1])

        return MarketDataResponse(
            symbol=symbol,
            current_price=current_price,
            ltf_rsi=RSIData(
                period="4H",
                rsi_value=ltf_rsi_val,
                status=get_rsi_label(ltf_rsi_val)
            ),
            htf_rsi=RSIData(
                period="Daily",
                rsi_value=daily_rsi_val,
                status=get_rsi_label(daily_rsi_val)
            )
        )

    except Exception as e:
        print(f"Piyasa verisi alınamadı ({yf_symbol}): {e}")
        return MarketDataResponse(
            symbol=symbol,
            current_price=None,
            ltf_rsi=RSIData(period="4H", rsi_value=None, status="Veri Yok"),
            htf_rsi=RSIData(period="Daily", rsi_value=None, status="Veri Yok")
        )

def get_chart_data(symbol: str) -> List[OHLCVCandle]:
    """Grafik OHLCV verisi çeker. Birden fazla sembol formatı dener."""
    try:
        hist = _try_fetch_history(symbol, period="1y", interval="1d")
        
        if hist.empty:
            print(f"Grafik verisi bulunamadı: {symbol}")
            return []
            
        candles = []
        for index, row in hist.iterrows():
            # Convert timestamp to YYYY-MM-DD
            date_str = index.strftime('%Y-%m-%d')
            
            candles.append(OHLCVCandle(
                time=date_str,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            ))
            
        return candles

    except Exception as e:
        print(f"Grafik verisi alınamadı ({symbol}): {e}")
        return []
