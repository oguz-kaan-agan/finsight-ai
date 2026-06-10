# 📈 FinSight AI

FinSight AI, finansal haber akışlarını gerçek zamanlı takip eden, yapay zeka (Google Gemini) ile duyarlılık (sentiment) analizi yapan ve teknik indikatörlerle (RSI) desteklenen web tabanlı bir finansal karar destek platformudur.

🔗 **Canlı Site:** [https://finsight-ai.vercel.app](https://finsight-ai.vercel.app)  
⚙️ **Admin Paneli:** [https://finsight-ai.vercel.app/admin](https://finsight-ai.vercel.app/admin)

---

## 🚀 Öne Çıkan Özellikler

- **AI Sentiment Analizi:** Haberlerin Gemini API ile Pozitif, Negatif veya Nötr olarak sınıflandırılması.
- **Teknik Analiz (RSI):** Hisseler için 4 Saatlik ve Günlük periyotlarda RSI (14) hesabı.
- **TradingView Grafik Entegrasyonu:** Detay panelinde TradingView mum grafikleri ve hacim takibi.
- **Admin Yönetim Paneli:** Dinamik RSS kaynağı yönetimi ve manuel haber girişi.
- **Modern Arayüz:** Koyu/açık tema desteği ve premium mikro etkileşimler.

---

## 🛠️ Teknoloji Yığını

- **Frontend:** React, Next.js (App Router), TypeScript, Tailwind CSS, lightweight-charts
- **Backend:** Python, FastAPI, SQLite, yfinance, Google Generative AI SDK

---

## ⚙️ Kurulum ve Çalıştırma

### 1. Çevre Değişkenleri
`backend/.env` dosyasını oluşturun:
```env
GEMINI_API_KEY=your_gemini_api_key
ADMIN_PASSWORD=your_admin_password
TOKEN_SECRET=your_jwt_secret
```

### 2. Başlatma (Local)
Proje kök dizinindeki `start.bat` dosyasını çalıştırarak yerel sunucuları başlatabilirsiniz.

---

## 📊 Teknik Analiz Standartları (RSI)
- **RSI < 30 (Ucuz):** Canlı Yeşil Rozet
- **30 <= RSI <= 70 (Nötr):** Soft Gri Rozet
- **RSI > 70 (Pahalı):** Canlı Kırmızı Rozet

---

## 👨‍💻 Geliştirici
- **Oğuz Kaan Ağan**  
- **E-posta:** oguzkaanagan2016@gmail.com  
- **Telefon:** 0536 490 99 59
