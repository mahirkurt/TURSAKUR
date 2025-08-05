#!/bin/bash
# React development server başlatma scripti

echo "🚀 TURSAKUR React uygulaması başlatılıyor..."
echo "📍 Dizin: $(pwd)"
echo "📦 Node.js versiyonu: $(node --version)"
echo "📦 npm versiyonu: $(npm --version)"

echo ""
echo "🔧 Bağımlılıkları kontrol ediliyor..."
if [ ! -d "node_modules" ]; then
    echo "📥 Bağımlılıklar yükleniyor..."
    npm install
fi

echo ""
echo "🌟 Development server başlatılıyor..."
echo "🌐 Tarayıcınızda http://localhost:5173 adresini açın"
echo ""

npm run dev
