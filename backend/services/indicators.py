import yfinance as yf
import pandas as pd
from services.market_data_service import normalize_symbol

def get_rsi_status(symbol: str, period: int = 14) -> str:
    """
    Belirtilen hisse sembolü için 14 günlük RSI değerini hesaplar ve 
    'Ucuz', 'Nötr' veya 'Pahalı' durumunu döndürür.
    """
    try:
        yf_symbol = normalize_symbol(symbol)
        
        # Son 3 aylık veriyi çekiyoruz (14 günlük RSI hesabı için yeterli)
        ticker = yf.Ticker(yf_symbol)
        history = ticker.history(period="3mo")
        
        if history.empty or len(history) < period + 1:
            return "Veri Yetersiz"
            
        close_prices = history['Close']
        
        # Günlük değişimler
        delta = close_prices.diff()
        
        # Pozitif ve negatif değişimler
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        # Üssel Hareketli Ortalama (EMA) ile RSI hesabı (standart yöntem)
        roll_up = up.ewm(com=period - 1, adjust=False).mean()
        roll_down = down.ewm(com=period - 1, adjust=False).mean()
        
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        # En güncel RSI değeri
        latest_rsi = rsi.iloc[-1]
        
        if pd.isna(latest_rsi):
            return "Hesaplanamadı"
            
        if latest_rsi < 30:
            return "Ucuz"
        elif latest_rsi > 70:
            return "Pahalı"
        else:
            return "Nötr"
            
    except Exception as e:
        print(f"RSI hesaplanırken hata oluştu ({symbol}): {e}")
        return "Hata"
