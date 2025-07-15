# TURSAKUR Dual Deployment Script
# Firebase + GitHub Pages deployment automation

Write-Host "🚀 TURSAKUR Dual Deployment Başlatılıyor..." -ForegroundColor Green
Write-Host "=" * 60

# 1. GitHub Secrets kontrolü
Write-Host "`n📋 GitHub Secrets Kontrolü:" -ForegroundColor Yellow
Write-Host "Gerekli secrets:"
Write-Host "  ✓ FIREBASE_TOKEN (Firebase CLI authentication)"
Write-Host "  ✓ Otomatik: GITHUB_TOKEN (GitHub Pages için)"

$continue = Read-Host "`nFirebase token'ını GitHub Secrets'a eklediniz mi? (y/n)"
if ($continue -ne "y") {
    Write-Host "`n❌ Deployment durduruldu. Önce Firebase token'ını ekleyin:" -ForegroundColor Red
    Write-Host "1. Firebase CLI'da: firebase login:ci"
    Write-Host "2. GitHub repo > Settings > Secrets and variables > Actions"
    Write-Host "3. FIREBASE_TOKEN secret'ını ekleyin"
    exit 1
}

# 2. Production build
Write-Host "`n🔨 Production Build Oluşturuluyor..." -ForegroundColor Cyan
python build.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build başarısız!" -ForegroundColor Red
    exit 1
}

# 3. Local verification
Write-Host "`n🔍 Local Verification..." -ForegroundColor Cyan
Write-Host "Build dosyaları kontrol ediliyor..."

$buildDir = "_build"
if (!(Test-Path $buildDir)) {
    Write-Host "❌ Build dizini bulunamadı!" -ForegroundColor Red
    exit 1
}

$requiredFiles = @("index.html", "map.html", "js/app.js", "data/turkiye_saglik_kuruluslari.json")
foreach ($file in $requiredFiles) {
    if (!(Test-Path "$buildDir/$file")) {
        Write-Host "❌ Eksik dosya: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Tüm build dosyaları hazır!" -ForegroundColor Green

# 4. Git push (GitHub Actions'ı tetiklemek için)
Write-Host "`n📤 GitHub'a Push Ediliyor..." -ForegroundColor Cyan
git add .
git commit -m "🚀 Deploy TURSAKUR v2.0.3 with dual deployment strategy

- Interactive maps with Leaflet.js
- Advanced search with autocomplete
- UX enhancements and animations
- Optimized production build
- Dual deployment: Firebase + GitHub Pages
- Full CI/CD automation"

git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git push başarısız!" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 GitHub Actions Workflow tetiklendi!" -ForegroundColor Green
Write-Host "📊 Deployment durumunu takip edin:"
Write-Host "  • GitHub > Actions sekmesi"
Write-Host "  • Dual Deployment workflow"

# 5. Deployment URL'leri
Write-Host "`n🌐 Deployment URL'leri:" -ForegroundColor Yellow
Write-Host "📱 PRIMARY (Firebase):   https://tursakur-healthcare.web.app"
Write-Host "🔄 BACKUP (GitHub):      https://[username].github.io/TURSAKUR"

Write-Host "`n⏱️ Deployment süresi: ~3-5 dakika"
Write-Host "✅ Dual deployment strategy aktif!"
Write-Host "🎊 TURSAKUR v2.0.3 yayına hazır!"
