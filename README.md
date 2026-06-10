# FinSight AI - Finansal Haber Sentiment Analizi ve Karar Destek Platformu

FinSight AI, finansal haber akışlarını gerçek zamanlı olarak takip eden, haberleri gelişmiş yapay zeka entegrasyonu (Google Gemini API) ile analiz ederek sektörel etki ve duyarlılık (sentiment) skorları üreten web tabanlı bir finansal karar destek platformudur. 

Platform, AI analizinin yanı sıra etkilenen finansal araçlar için (hisseler, emtialar, kripto paralar vb.) kısa vadeli (4 Saatlik) ve uzun vadeli (Günlük) zaman dilimlerinde RSI (Relative Strength Index) indikatörlerini hesaplayarak teknik görünüm (Ucuz / Nötr / Pahalı) sunar ve detay panelinde TradingView grafik entegrasyonu barındırır.

---

## 🚀 Özellikler

- **Gerçek Zamanlı Haber Akışı:** RSS kaynaklarından ve manuel olarak girilen haberlerden derlenen dinamik akış.
- **Yapay Zeka Destekli Sentiment Analizi:** Gemini API (Structured Outputs) kullanılarak haberlerin Pozitif, Negatif veya Nötr olarak sınıflandırılması.
- **Sektörel ve Enstrüman Bazlı Eşleştirme:** Haber içeriğinden etkilenen sektörlerin ve finansal araçların (BIST, ABD Borsaları, Kripto, Döviz, Emtia) otomatik tespiti.
- **Çoklu Zaman Dilimli RSI Analizi:** Teknik görünümün hızlı tespiti için 4 Saatlik (LTF) ve Günlük (HTF) periyotlarda programatik RSI (14) hesabı.
- **TradingView Grafik Entegrasyonu:** Enstrüman detay panelinde TradingView Advanced Chart aracı ile profesyonel grafik takibi.
- **Yönetici Paneli (Admin Dashboard):** Şifre korumalı yönetim panelinde RSS kaynakları ekleme/çıkarma/düzenleme, manuel haber girişi ve genel site ayarlarının yönetimi.
- **Modern Koyu/Açık Tema UI/UX:** Hızlı arama, sektörel filtreler, responsive tasarım ve premium hissi veren mikro etkileşimler.

---

## 🛠️ Teknoloji Yığını

### Backend
- **Framework:** Python / FastAPI (Asenkron mimari)
- **Veri Analizi & Hesaplama:** `yfinance` (Tarihsel fiyat ve RSI analizi)
- **Yapay Zeka:** Google Generative AI SDK (Gemini-2.5-flash)
- **Veritabanı:** SQLite & Pydantic Modelleri
- **Kimlik Doğrulama:** JWT Tabanlı Admin Auth

### Frontend
- **Framework:** React.js / Next.js (App Router, TypeScript)
- **Stil & Arayüz:** Tailwind CSS & Radix UI (shadcn/ui standartları)
- **Grafik & Görselleştirme:** TradingView Advanced Widget, lightweight-charts, Three.js / WebGL arka plan efektleri
- **Veri Yönetimi:** TanStack Query (React Query)
- **İkonlar:** Lucide React

---

## 📂 Proje Yapısı

```text
haber/
├── backend/
│   ├── services/
│   │   ├── ai_service.py           # Gemini API entegrasyonu ve mock analiz servisi
│   │   ├── indicators.py           # RSI teknik analiz hesaplamaları
│   │   ├── market_data_service.py  # yfinance veri çekme ve grafik verisi hazırlama
│   │   └── news_service.py         # Haber akışı çekme ve RSS işlemleri
│   ├── auth.py                     # Yönetici kimlik doğrulama işlemleri
│   ├── database.py                 # SQLite veritabanı şeması ve CRUD işlemleri
│   ├── main.py                     # API uç noktaları (Endpoints) ve arka plan haber döngüsü
│   ├── models.py                   # Pydantic veri modelleri
│   ├── requirements.txt            # Python bağımlılıkları
│   └── .env.example                # Örnek çevre değişkenleri
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router sayfaları (Main & Admin)
│   │   ├── components/             # Yeniden kullanılabilir UI bileşenleri ve WebGL efektleri
│   │   ├── hooks/                  # Özel React hook'ları
│   │   └── lib/                    # API istemcisi ve yardımcı fonksiyonlar
│   ├── package.json                # Frontend paket bağımlılıkları
│   └── tsconfig.json               # TypeScript yapılandırması
│
└── start.bat                       # Hem Backend hem Frontend'i tek tıkla başlatan betik
```

---

## 🔧 Kurulum ve Çalıştırma

### 1. Backend Kurulumu

Gerekli Python bağımlılıklarını yükleyin ve çevresel değişkenleri ayarlayın:

```bash
cd backend
python -m venv venv
# Windows için:
venv\Scripts\activate
# macOS/Linux için:
source venv/bin/activate

pip install -r requirements.txt
```

`backend` dizini altında `.env` dosyası oluşturun ve gerekli değerleri girin (örnek için `.env.example` dosyasını inceleyebilirsiniz):

```env
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_PASSWORD=admin123
SECRET_KEY=any_random_secret_string
```

Backend sunucusunu başlatmak için:

```bash
python main.py
```
API, varsayılan olarak `http://localhost:8000` adresinde çalışacaktır.

---

### 2. Frontend Kurulumu

Bağımlılıkları yükleyin ve Next.js geliştirme sunucusunu çalıştırın:

```bash
cd frontend
npm install
npm run dev
```

Frontend, varsayılan olarak `http://localhost:3000` adresinde çalışacaktır.

---

### 3. Kolay Başlatma (Windows)

Proje kök dizininde bulunan `start.bat` dosyasını çalıştırarak hem backend hem de frontend sunucularını aynı anda başlatabilir ve tarayıcınızda uygulamayı otomatik olarak açabilirsiniz.

---

## 📊 Teknik Analiz Mantığı (RSI)

Platform, yapay zekanın tespit ettiği finansal semboller için matematiksel RSI (14) indikatörünü hesaplayarak yatırımcıya nesnel bir görünüm sunar:
- **RSI < 30 (Aşırı Satım / Ucuz):** Fiyatın kısa vadede tepki yükselişi yapabileceğini belirtir. Arayüzde **Yeşil** renkli rozetle gösterilir.
- **30 <= RSI <= 70 (Nötr):** Fiyatın dengeli veya yatay trendde olduğunu belirtir. Arayüzde **Gri** renkli rozetle gösterilir.
- **RSI > 70 (Aşırı Alım / Pahalı):** Fiyatın kısa vadede düzeltme yiyebileceğini belirtir. Arayüzde **Kırmızı** renkli rozetle gösterilir.

---

## 📝 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için lisans dosyasına göz atabilirsiniz.
