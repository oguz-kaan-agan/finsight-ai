@echo off
echo FinSight AI Baslatiliyor...

echo Backend (Python) baslatiliyor...
start cmd /k "cd backend && python main.py"

echo Frontend (Next.js) baslatiliyor...
start cmd /k "cd frontend && npm run dev"

echo Lutfen sunucularin hazir olmasi icin 5 saniye bekleyin...
timeout /t 5 /nobreak > nul

echo Tarayici otomatik olarak aciliyor...
start http://localhost:3000

echo ========================================================
echo Her iki sistem de ayri pencerelerde baslatildi!
echo Tarayiciniz otomatik olarak siteyi acacaktir.
echo Acilmazsa manuel olarak su adreslere gidebilirsiniz:
echo Site: http://localhost:3000
echo Admin Paneli: http://localhost:3000/admin
echo ========================================================
pause
