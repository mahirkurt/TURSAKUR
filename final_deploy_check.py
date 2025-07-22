#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Öncesi Final Kontrolü
Sistemin canlıya çıkmaya hazır olduğunu doğrular
"""

import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def final_deploy_check():
    """Deploy öncesi final kontrol"""
    
    logger.info("🚀 DEPLOY ÖNCESİ FİNAL KONTROL")
    logger.info("=" * 50)
    
    checks = {
        "ana_veri": False,
        "web_dosyalar": False,
        "github_actions": False,
        "requirements": False,
        "scripts": False
    }
    
    # Ana veri kontrolü
    try:
        with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        kurum_count = len(data.get('kurumlar', []))
        il_count = data.get('meta', {}).get('toplam_il', 0)
        
        if kurum_count > 1000 and il_count >= 81:
            checks["ana_veri"] = True
            logger.info(f"✅ Ana veri: {kurum_count} kurum, {il_count} il")
        else:
            logger.error(f"❌ Ana veri: Yetersiz - {kurum_count} kurum, {il_count} il")
            
    except Exception as e:
        logger.error(f"❌ Ana veri okunamadı: {e}")
    
    # Web dosyaları kontrolü
    web_files = ['index.html', 'js/app.js', 'styles/main.css']
    web_ok = True
    
    for file_path in web_files:
        if os.path.exists(file_path):
            logger.info(f"✅ Web dosyası: {file_path}")
        else:
            logger.error(f"❌ Web dosyası eksik: {file_path}")
            web_ok = False
    
    checks["web_dosyalar"] = web_ok
    
    # GitHub Actions kontrolü
    workflow_path = '.github/workflows/data-processing.yml'
    if os.path.exists(workflow_path):
        checks["github_actions"] = True
        logger.info(f"✅ GitHub Actions: {workflow_path}")
    else:
        logger.error(f"❌ GitHub Actions eksik: {workflow_path}")
    
    # Requirements kontrolü
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            reqs = f.read()
        if 'requests' in reqs and 'pandas' in reqs:
            checks["requirements"] = True
            logger.info("✅ Requirements.txt: Gerekli paketler mevcut")
        else:
            logger.error("❌ Requirements.txt: Eksik paketler")
    else:
        logger.error("❌ Requirements.txt bulunamadı")
    
    # Kritik scriptler kontrolü
    critical_scripts = [
        'scripts/validate_data.py',
        'scripts/process_data.py',
        'scripts/fetch_saglik_bakanligi_data.py',
        'quick_syntax_check.py',
        'fix_cankiri.py',
        'clean_all_data.py'
    ]
    
    scripts_ok = True
    for script in critical_scripts:
        if os.path.exists(script):
            logger.info(f"✅ Script: {script}")
        else:
            logger.error(f"❌ Script eksik: {script}")
            scripts_ok = False
    
    checks["scripts"] = scripts_ok
    
    # Genel sonuç
    success_count = sum(checks.values())
    total_count = len(checks)
    
    logger.info(f"\n📊 SONUÇ: {success_count}/{total_count} kontrol başarılı")
    
    if success_count == total_count:
        logger.info("🎉 SİSTEM DEPLOY'A HAZIR!")
        logger.info("✅ Tüm kontroller başarılı")
        logger.info("🚀 GitHub'a push yapabilirsiniz")
        return True
    else:
        logger.error("⚠️ SİSTEMDE SORUNLAR VAR!")
        logger.error("❌ Eksiklikleri giderin")
        return False

if __name__ == "__main__":
    success = final_deploy_check()
    exit(0 if success else 1)
