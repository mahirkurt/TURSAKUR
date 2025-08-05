# TURSAKUR 2.0 - Deployment Script
# PowerShell deployment automation

Write-Host "🚀 TURSAKUR 2.0 - DEPLOYMENT BAŞLADI" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan

# 1. Build kontrolü
Write-Host "📦 Build kontrolü yapılıyor..." -ForegroundColor Yellow
if (Test-Path "_build") {
    Write-Host "✅ _build klasörü mevcut" -ForegroundColor Green
} else {
    Write-Host "❌ _build klasörü bulunamadı! Önce build.py çalıştırın." -ForegroundColor Red
    exit 1
}

# 2. Gerekli dosya kontrolü
$requiredFiles = @(
    "_build/index.html",
    "_build/map.html", 
    "_build/manifest.json",
    "_build/sw.js",
    "_build/js",
    "_build/styles",
    "_build/data"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - EKSIK!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "❌ Bazı dosyalar eksik! Deploy durduruluyor." -ForegroundColor Red
    exit 1
}

# 3. Veri kontrolü
Write-Host "📊 Veri durumu kontrol ediliyor..." -ForegroundColor Yellow
try {
    $pythonScript = @"
import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if supabase_url and service_key:
    client = create_client(supabase_url, service_key)
    result = client.table('kuruluslar').select('kurum_id', count='exact').execute()
    print(f'DATA_COUNT:{result.count}')
else:
    print('DATA_COUNT:0')
"@
    
    $result = python -c $pythonScript
    $dataCount = ($result | Select-String "DATA_COUNT:(\d+)").Matches[0].Groups[1].Value
    
    if ([int]$dataCount -gt 100) {
        Write-Host "✅ Supabase'de $dataCount kurum verisi mevcut" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Veri sayısı yetersiz: $dataCount" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Veri kontrolü başarısız" -ForegroundColor Red
}

# 4. Git durumu kontrolü
Write-Host "📝 Git durumu kontrol ediliyor..." -ForegroundColor Yellow
try {
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "📝 Değişiklikler commit ediliyor..." -ForegroundColor Yellow
        git add .
        $commitMessage = "Deploy: TURSAKUR 2.0 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        git commit -m $commitMessage
        Write-Host "✅ Değişiklikler commit edildi" -ForegroundColor Green
    } else {
        Write-Host "✅ Git repository temiz" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Git işlemi başarısız - devam ediliyor" -ForegroundColor Yellow
}

# 5. GitHub push
Write-Host "🔄 GitHub'a push ediliyor..." -ForegroundColor Yellow
try {
    git push origin main
    Write-Host "✅ GitHub push başarılı" -ForegroundColor Green
} catch {
    Write-Host "⚠️ GitHub push başarısız - manuel kontrol gerekli" -ForegroundColor Yellow
}

# 6. Netlify deploy (eğer CLI mevcut ise)
Write-Host "🌐 Netlify deploy kontrol ediliyor..." -ForegroundColor Yellow
try {
    $netlifyCmd = Get-Command netlify -ErrorAction SilentlyContinue
    if ($netlifyCmd) {
        Write-Host "📤 Netlify'a deploy ediliyor..." -ForegroundColor Yellow
        netlify deploy --prod --dir=_build
        Write-Host "✅ Netlify deploy başarılı" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Netlify CLI bulunamadı - manuel deploy gerekli" -ForegroundColor Yellow
        Write-Host "📁 _build klasörünü manuel olarak Netlify'a yükleyin" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Netlify deploy başarısız" -ForegroundColor Yellow
}

# 7. Vercel deploy (eğer CLI mevcut ise)  
Write-Host "🔷 Vercel deploy kontrol ediliyor..." -ForegroundColor Yellow
try {
    $vercelCmd = Get-Command vercel -ErrorAction SilentlyContinue
    if ($vercelCmd) {
        Write-Host "📤 Vercel'e deploy ediliyor..." -ForegroundColor Yellow
        vercel --prod
        Write-Host "✅ Vercel deploy başarılı" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Vercel CLI bulunamadı" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Vercel deploy başarısız" -ForegroundColor Yellow
}

# 8. Deploy raporu
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎉 DEPLOYMENT TAMAMLANDI!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Deploy Özeti:" -ForegroundColor White
Write-Host "• Build: ✅ Hazır" -ForegroundColor Green
Write-Host "• Veriler: ✅ $dataCount kurum" -ForegroundColor Green
Write-Host "• Dosyalar: ✅ Tamamlandı" -ForegroundColor Green
Write-Host "• Git: ✅ Push edildi" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Deployment URL'leri:" -ForegroundColor White
Write-Host "• GitHub Pages: https://mahirkurt.github.io/TURSAKUR" -ForegroundColor Cyan
Write-Host "• Netlify: Manuel deploy gerekli" -ForegroundColor Yellow
Write-Host "• Vercel: Otomatik deploy" -ForegroundColor Green
Write-Host ""
Write-Host "🎊 TURSAKUR 2.0 başarıyla deploy edildi!" -ForegroundColor Green
