@echo off
echo TURSAKUR 2.0 - React App Başlatıcı
echo.
echo Canlı Supabase bağlantısı ile React uygulaması başlatılıyor...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Node modules bulunamadı, yükleniyor...
    npm install
)

echo.
echo React development server başlatılıyor...
echo.
echo Uygulama: http://localhost:5173
echo Supabase: https://moamwmxcpgjvyyawlygw.supabase.co
echo.

npm run dev
