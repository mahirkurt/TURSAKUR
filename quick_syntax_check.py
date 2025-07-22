#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı Script Syntax Kontrolü
"""

import ast
import os
import sys

def check_python_syntax(file_path):
    """Python dosyasının syntax'ını kontrol et"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # AST ile syntax kontrolü
        ast.parse(source, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Ana kontrol fonksiyonu"""
    scripts_dir = "scripts"
    critical_scripts = [
        "fetch_saglik_bakanligi_data.py",
        "fetch_ozel_hastaneler_data.py", 
        "fetch_universite_hastaneleri.py",
        "validate_data.py",
        "process_data.py"
    ]
    
    print("🔍 KRİTİK SCRİPT SYNTAX KONTROLÜ")
    print("=" * 50)
    
    all_good = True
    
    for script in critical_scripts:
        script_path = os.path.join(scripts_dir, script)
        
        if not os.path.exists(script_path):
            print(f"❌ {script} - Dosya bulunamadı")
            all_good = False
            continue
        
        is_valid, error = check_python_syntax(script_path)
        
        if is_valid:
            print(f"✅ {script} - Syntax OK")
        else:
            print(f"❌ {script} - Syntax HATA: {error}")
            all_good = False
    
    print(f"\n{'🎉 TÜM SCRİPTLER SYNTAX OK!' if all_good else '⚠️ SYNTAX HATALARI VAR!'}")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
