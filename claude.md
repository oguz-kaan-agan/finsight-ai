# Project Overview
Bu proje, finansal haber akışlarını anlık olarak takip eden, bu haberleri yapay zeka (Gemini) ile analiz ederek duyarlılık (sentiment) skorları üreten ve haberlerin hangi finansal araçları (hisse senetleri, emtialar, kripto paralar) ve sektörleri etkileyebileceğini akıllıca tahmin eden web tabanlı bir finansal karar destek platformudur. 

Kullanıcılar, haber akışında listelenen ve AI tarafından tespit edilen "etkilenen finansal araçlara" tıkladıklarında, sistem arka planda programatik bir teknik analiz gerçekleştirecektir. Bu analiz, hem kısa vadeli (LTF - 4 Saatlik) hem de uzun vadeli (HTF - Günlük) zaman dilimlerinde RSI (Relative Strength Index) indikatörünü hesaplayarak fiyata "Ucuz" (Yeşil), "Nötr" (Gri) veya "Pahalı" (Kırmızı) etiketleri atayacaktır. Detay panelinde TradingView grafik entegrasyonu yer alacak, böylece kullanıcılar ücretsiz ve profesyonel grafiklere anında erişebilecektir. Arayüz, en güncel haberlerin en üste düştüğü, gelişmiş arama ve sektörel/isim bazlı filtreleme özelliklerine sahip, yüksek kaliteli (premium UI/UX) bir tasarıma sahip olacaktır.

## Tech Stack
- **Frontend Framework:** React.js (Next.js App Router tercih edilmeli, TypeScript ile tip güvenliği sağlanmalı)
- **Styling & UI Library:** Tailwind CSS + shadcn/ui (Modern, temiz ve finans platformlarına uygun koyu/açık tema bileşenleri)
- **Icons:** Lucide React
- **State Management & Data Fetching:** TanStack Query (React Query) veya native React Context API
- **Backend Framework:** Python (FastAPI) - Asenkron yapısı ve veri bilimi/finans kütüphaneleriyle tam uyumu için
- **AI / LLM Integration:** Google Gemini API (Antigravity entegrasyonu üzerinden) - Yapılandırılmış JSON çıktı modu (Structured Outputs) kullanılacak
- **Market Data & Math Logic:** `yfinance` (Yahoo Finance API) - Ücretsiz tarihsel fiyat verileri ve teknik indikatör hesaplamaları için
- **News Aggregator:** NewsAPI, RSS Finans Feedleri veya Yahoo Finance Scraping/API çözümleri
- **Charts Component:** TradingView Advanced Chart Widget (HTML/JS Embed) veya TradingView Lightweight Charts

## Coding Rules
1. **Modüler ve Fonksiyonel React Bileşenleri:** Tüm frontend bileşenleri fonksiyonel olmalı, hooks (`useState`, `useEffect`, `useMemo`, `useCallback`) performansı optimize edecek şekilde kullanılmalıdır. Kod tekrarından kaçınılmalı, her bileşen tek bir sorumluluğa (Single Responsibility) sahip olmalıdır.
2. **Eksiksiz TypeScript Tanımlamaları:** Haber nesnesi, AI analiz sonucu, teknik analiz verileri ve filtreleme state'leri için kesinlikle arayüzler (`interfaces`) veya tipler (`types`) tanımlanmalıdır. `any` kullanımı yasaktır.
3. **Sıkı Tailwind ve UI Kuralları:** `style={{ ... }}` şeklinde inline stil kullanımı kesinlikle yasaktır. Tüm görsel düzen Tailwind CSS sınıflarıyla yönetilmelidir. Kartlar, butonlar ve paneller için shadcn/ui standartları korunmalı, mikro etkileşimler ve yumuşak geçiş efektleri (transitions) eklenmelidir.
4. **Yapılandırılmış Yapay Zeka Çıktısı (Structured JSON):** Gemini'a gönderilecek prompt'lar, modelin yanıtı kesinlikle aşağıda belirtilen JSON şemasında döndürmesini zorunlu kılmalıdır (`response_mime_type: "application/json"`). Yapay zekanın serbest metin üretmesine izin verilmemelidir.
   ```json
   {
     "sentiment": "Positive" | "Negative" | "Neutral",
     "affected_sectors": ["Teknoloji", "Havacılık", "Enerji", vb.],
     "affected_instruments": ["THYAO", "PGSUS", "AAPL", "BTC", vb.],
     "impact_summary": "Haberin enstrümanlar üzerindeki etkisinin kısa mantıksal açıklaması."
   }
   ```
5. **Programatik RSI Analiz Mantığı:** Karmaşık ve subjektif finansal yorumlar yerine, enstrümanın ucuz veya pahalı olma durumu tamamen matematiksel RSI (14) değerine bağlanacaktır:
   - **RSI < 30:** Ucuz (UI görünümü: Canlı Yeşil Rozet / Metin, `#22c55e`)
   - **30 <= RSI <= 70:** Nötr (UI görünümü: Yumuşak Gri Rozet / Metin, `#64748b`)
   - **RSI > 70:** Pahalı (UI görünümü: Canlı Kırmızı Rozet / Metin, `#ef4444`)
6. **Haber Akışı ve Performans:** Yeni gelen haberler animasyonlu bir şekilde listenin en üstüne eklenmeli, eski haberler aşağı kaymalıdır. Sayfalama (Pagination) veya Sonsuz Kaydırma (Infinite Scroll) altyapısı kurulmalıdır.
7. **Hata ve Yükleme Yönetimi:** API istekleri sırasında ekran donmamalı; skeleton loader yapısı kullanılmalıdır. Olası API kesintilerinde (Örn: yfinance veya Gemini kota aşımı) kullanıcıya temiz hata mesajları ve fallback veriler sunulmalıdır.

## Memory
### Alınan Kritik Kararlar
- **TradingView Çözümü:** Grafikleri sıfırdan çizmek yerine TradingView Advanced Chart Widget yapısı iframe/script injection ile entegre edilecektir. Bu sayede indikatörler, hacim ve mum grafikleri ücretsiz ve eksiksiz olarak frontend'de gösterilecektir.
- **Zaman Dilimleri (Multi-Timeframe):** Teknik analiz durumunun net anlaşılması için her enstrüman için hem 4H (LTF - Yakın Vade) hem de Daily (HTF - Ana Trend) RSI değerleri ayrı ayrı hesaplanıp yan yana gösterilecektir.
- **Gelişmiş Arama ve Filtreleme Paneli:** Arayüzün üst kısmında kullanıcıların haber başlıklarında arama yapabileceği bir input alanı ve sektörlere (Havacılık, Bankacılık, Teknoloji, Kripto vb.) göre hızlı filtreleme yapabileceği dinamik tag'ler/butonlar bulunacaktır.
- **Sektörel Etki Görselleştirmesi:** Haber kartlarında sadece hisse kodu değil, haberi tetikleyen ana sektör de bir etiket olarak vurgulanacaktır.

### Durum Takibi (Yapılacaklar / Yol Haritası)
- [ ] **Aşama 1: Proje Kurulumu & Backend Altyapısı**
  - [ ] FastAPI projesinin iskeletinin oluşturulması ve gerekli kütüphanelerin (`fastapi`, `uvicorn`, `yfinance`, `google-generativeai`, `pydantic`) yüklenmesi.
  - [ ] Haber akışını simüle eden veya API/RSS üzerinden çeken servis kodunun yazılması.
- [ ] **Aşama 2: AI Entegrasyonu & Karar Motoru**
  - [ ] Gemini API bağlantısının kurulması ve yapılandırılmış JSON modunun aktifleştirilmesi.
  - [ ] Finansal haberleri sentiment, sektör ve enstrüman bazında ayrıştıran sistem prompt'unun mükemmelleştirilmesi.
- [ ] **Aşama 3: Piyasa Verisi & Teknik Göstergeler**
  - [ ] `yfinance` üzerinden gelen sembole göre son fiyat bilgisini çeken fonksiyonun yazılması.
  - [ ] Gelen sembol için 4H ve Daily periyotlarda 14 günlük RSI hesaplayan matematiksel servisin tamamlanması.
- [ ] **Aşama 4: Frontend Arayüz Tasarımı (UI/UX)**
  - [ ] Next.js projesinin kurulması, Tailwind CSS ve shadcn/ui kütüphanelerinin entegre edilmesi.
  - [ ] Üst bar (Arama ve Sektör Filtreleri) ve Kronolojik Haber Akışı (Feed) bileşenlerinin tasarlanması.
  - [ ] Haber kartlarının duyarlılık renklerine göre (Pozitif: Yeşil kenarlık/gölge, Negatif: Kırmızı) görselleştirilmesi.
- [ ] **Aşama 5: Detay Paneli & Grafik Entegrasyonu**
  - [ ] Bir habere veya enstrümana tıklandığında sağdan açılan panel (Drawer/Sheet) veya modal yapısının kurulması.
  - [ ] Bu panel içinde LTF (4H) ve HTF (Daily) RSI durumlarının (Ucuz/Nötr/Pahalı) renkli indikatörlerle gösterilmesi.
  - [ ] Seçili enstrümanın koduna göre dinamik olarak güncellenen TradingView Widget'ının yerleştirilmesi.
- [ ] **Aşama 6: Entegrasyon ve Test**
  - [ ] Frontend ile Backend API endpoints'lerinin buluşturulması.
  - [ ] Uçtan uca veri akışının, filtreleme performansının ve AI tepki sürelerinin optimize edilmesi.
