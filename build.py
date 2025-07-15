#!/usr/bin/env python3
"""
TURSAKUR Production Build Script
Optimizes and prepares the application for deployment
"""

import os
import json
import shutil
import datetime
import hashlib
from pathlib import Path
import re

class ProductionBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.build_dir = self.root_dir / '_build'
        self.version = "2.0.3"
        self.build_time = datetime.datetime.utcnow().isoformat() + 'Z'
        
    def clean_build_dir(self):
        """Clean and create build directory"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir()
        print("✅ Build directory cleaned")
        
    def copy_assets(self):
        """Copy necessary files to build directory"""
        # Files to copy
        files_to_copy = [
            'index.html',
            'map.html',
            'manifest.json',
            'sw.js',
            'favicon.svg'
        ]
        
        # Directories to copy
        dirs_to_copy = [
            'js',
            'css', 
            'styles',
            'data',
            'assets'
        ]
        
        # Copy files
        for file in files_to_copy:
            if (self.root_dir / file).exists():
                shutil.copy2(self.root_dir / file, self.build_dir / file)
                print(f"📄 Copied {file}")
                
        # Copy directories
        for dir_name in dirs_to_copy:
            src_dir = self.root_dir / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, self.build_dir / dir_name)
                print(f"📁 Copied {dir_name}/")
                
    def optimize_json(self):
        """Optimize JSON data files"""
        data_dir = self.build_dir / 'data'
        if not data_dir.exists():
            return
            
        for json_file in data_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Minify JSON (remove unnecessary whitespace)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                
                print(f"🗜️  Optimized {json_file.name}")
            except Exception as e:
                print(f"❌ Error optimizing {json_file.name}: {e}")
                
    def add_cache_busting(self):
        """Add cache busting to static assets"""
        # Get file hashes for cache busting
        asset_hashes = {}
        
        for file_path in self.build_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.js', '.css', '.json']:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                
                relative_path = file_path.relative_to(self.build_dir)
                asset_hashes[str(relative_path)] = file_hash
        
        # Update HTML files with cache busting
        for html_file in self.build_dir.glob('*.html'):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add version parameter to asset URLs
            for asset_path, hash_value in asset_hashes.items():
                old_path = asset_path
                new_path = f"{asset_path}?v={hash_value}"
                content = content.replace(f'"{old_path}"', f'"{new_path}"')
                content = content.replace(f"'{old_path}'", f"'{new_path}'")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("🏷️  Added cache busting to assets")
        
    def create_sitemap(self):
        """Create sitemap.xml for SEO"""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://mahirkurt.github.io/TURSAKUR/</loc>
        <lastmod>{}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://mahirkurt.github.io/TURSAKUR/map.html</loc>
        <lastmod>{}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>'''.format(self.build_time.split('T')[0], self.build_time.split('T')[0])
        
        with open(self.build_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print("🗺️  Created sitemap.xml")
        
    def create_robots_txt(self):
        """Create robots.txt"""
        robots_content = '''User-agent: *
Allow: /

Sitemap: https://mahirkurt.github.io/TURSAKUR/sitemap.xml
'''
        
        with open(self.build_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print("🤖 Created robots.txt")
        
    def create_build_info(self):
        """Create build information file"""
        build_info = {
            "version": self.version,
            "build_time": self.build_time,
            "build_type": "production",
            "features": [
                "interactive_map",
                "advanced_search", 
                "ux_enhancement",
                "material_design_3",
                "pwa_ready"
            ]
        }
        
        with open(self.build_dir / 'build-info.json', 'w', encoding='utf-8') as f:
            json.dump(build_info, f, indent=2)
        
        print("ℹ️  Created build info")
        
    def optimize_html(self):
        """Add meta tags and optimize HTML"""
        for html_file in self.build_dir.glob('*.html'):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add Open Graph and SEO meta tags if not present
            if 'og:title' not in content:
                meta_tags = '''
    <!-- SEO Meta Tags -->
    <meta name="description" content="Türkiye'deki tüm sağlık kuruluşlarının kapsamlı veritabanı. Hastaneler, sağlık merkezleri ve diş sağlığı merkezlerini kolayca bulun.">
    <meta name="keywords" content="hastane, sağlık merkezi, türkiye, sağlık kuruluşları, hastane arama">
    <meta name="author" content="TURSAKUR Team">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="TURSAKUR - Türkiye Sağlık Kuruluşları">
    <meta property="og:description" content="Türkiye'deki tüm sağlık kuruluşlarının kapsamlı veritabanı">
    <meta property="og:image" content="https://mahirkurt.github.io/TURSAKUR/assets/logos/TURSAKUR-Color.png">
    <meta property="og:url" content="https://mahirkurt.github.io/TURSAKUR/">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="tr_TR">
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="TURSAKUR - Türkiye Sağlık Kuruluşları">
    <meta name="twitter:description" content="Türkiye'deki tüm sağlık kuruluşlarının kapsamlı veritabanı">
    <meta name="twitter:image" content="https://mahirkurt.github.io/TURSAKUR/assets/logos/TURSAKUR-Color.png">'''
                
                # Insert meta tags before closing head tag
                content = content.replace('</head>', meta_tags + '\n</head>')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("📝 Optimized HTML with SEO meta tags")
        
    def build(self):
        """Main build process"""
        print("🚀 Starting TURSAKUR production build...")
        print(f"📦 Version: {self.version}")
        print(f"🕐 Build time: {self.build_time}")
        print()
        
        self.clean_build_dir()
        self.copy_assets()
        self.optimize_json()
        self.optimize_html()
        self.add_cache_busting()
        self.create_sitemap()
        self.create_robots_txt()
        self.create_build_info()
        
        print()
        print("✅ Production build completed successfully!")
        print(f"📁 Build output: {self.build_dir}")
        print("🌐 Ready for deployment!")

if __name__ == "__main__":
    builder = ProductionBuilder()
    builder.build()
