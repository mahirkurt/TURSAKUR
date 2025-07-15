#!/usr/bin/env python3
"""
TURSAKUR Deployment Verification Script
Checks if the deployment was successful and all features are working
"""

import requests
import json
import time
from urllib.parse import urljoin

class DeploymentVerifier:
    def __init__(self):
        self.base_urls = [
            "https://turkiye-sakur.web.app/",  # Firebase Hosting (PRIMARY)
            "https://mahirkurt.github.io/TURSAKUR/"  # GitHub Pages (BACKUP)
        ]
        self.endpoints_to_check = [
            "",  # Homepage
            "map.html",  # Map page
            "data/turkiye_saglik_kuruluslari.json",  # Main data
            "manifest.json",  # PWA manifest
            "build-info.json"  # Build information
        ]
        
    def check_url(self, url, timeout=10):
        """Check if URL is accessible and returns expected content"""
        try:
            response = requests.get(url, timeout=timeout)
            return {
                'url': url,
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', '')
            }
        except requests.RequestException as e:
            return {
                'url': url,
                'status_code': None,
                'accessible': False,
                'error': str(e),
                'content_length': 0,
                'content_type': ''
            }
    
    def verify_deployment(self, base_url):
        """Verify deployment for a specific base URL"""
        print(f"\n🔍 Verifying deployment: {base_url}")
        print("=" * 60)
        
        results = []
        for endpoint in self.endpoints_to_check:
            url = urljoin(base_url, endpoint)
            result = self.check_url(url)
            results.append(result)
            
            status_icon = "✅" if result['accessible'] else "❌"
            endpoint_name = endpoint if endpoint else "Homepage"
            
            print(f"{status_icon} {endpoint_name}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status_code']}")
            print(f"   Size: {result['content_length']} bytes")
            
            if not result['accessible'] and 'error' in result:
                print(f"   Error: {result['error']}")
            print()
        
        # Summary
        accessible_count = sum(1 for r in results if r['accessible'])
        total_count = len(results)
        success_rate = (accessible_count / total_count) * 100
        
        print(f"📊 Summary: {accessible_count}/{total_count} endpoints accessible ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Deployment verification PASSED!")
        else:
            print("⚠️ Deployment verification FAILED!")
        
        return success_rate >= 80
    
    def check_data_integrity(self, base_url):
        """Check if data files contain expected content"""
        print(f"\n📊 Checking data integrity for: {base_url}")
        print("=" * 60)
        
        data_url = urljoin(base_url, "data/turkiye_saglik_kuruluslari.json")
        try:
            response = requests.get(data_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    hospital_count = len(data)
                elif isinstance(data, dict) and 'kurumlar' in data:
                    hospital_count = len(data['kurumlar'])
                else:
                    hospital_count = 0
                
                print(f"✅ Data file accessible")
                print(f"📈 Hospital count: {hospital_count}")
                
                if hospital_count > 1000:
                    print("🎯 Data integrity CHECK PASSED!")
                    return True
                else:
                    print("⚠️ Data integrity CHECK FAILED - Low hospital count!")
                    return False
            else:
                print(f"❌ Data file not accessible (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Error checking data integrity: {e}")
            return False
    
    def check_build_info(self, base_url):
        """Check build information"""
        print(f"\n🏗️ Checking build info for: {base_url}")
        print("=" * 60)
        
        build_info_url = urljoin(base_url, "build-info.json")
        try:
            response = requests.get(build_info_url, timeout=10)
            if response.status_code == 200:
                build_info = response.json()
                
                print(f"✅ Build info accessible")
                print(f"📦 Version: {build_info.get('version', 'Unknown')}")
                print(f"🕐 Build time: {build_info.get('build_time', 'Unknown')}")
                print(f"🏷️ Build type: {build_info.get('build_type', 'Unknown')}")
                
                features = build_info.get('features', [])
                print(f"✨ Features ({len(features)}):")
                for feature in features:
                    print(f"   • {feature}")
                
                return True
            else:
                print(f"❌ Build info not accessible (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Error checking build info: {e}")
            return False
    
    def run_full_verification(self):
        """Run complete deployment verification"""
        print("🚀 TURSAKUR Dual Deployment Verification")
        print("=" * 60)
        print(f"🕐 Verification time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        print("🎯 Strategy: Dual Deployment (Firebase Primary + GitHub Pages Backup)")
        
        all_passed = True
        results = {}
        
        for i, base_url in enumerate(self.base_urls):
            platform = "Firebase Hosting" if i == 0 else "GitHub Pages"
            role = "PRIMARY" if i == 0 else "BACKUP"
            
            print(f"\n🔍 Verifying {platform} ({role})")
            print("=" * 60)
            
            # Basic deployment check
            deployment_ok = self.verify_deployment(base_url)
            
            # Data integrity check
            data_ok = self.check_data_integrity(base_url)
            
            # Build info check
            build_ok = self.check_build_info(base_url)
            
            url_passed = deployment_ok and data_ok
            results[platform.lower().replace(' ', '_')] = {
                'passed': url_passed,
                'deployment': deployment_ok,
                'data': data_ok,
                'build_info': build_ok,
                'url': base_url,
                'role': role
            }
            
            if not url_passed:
                all_passed = False
            
            status_icon = "🎉" if url_passed else "❌"
            print(f"\n{status_icon} {platform} ({role}): {'PASSED' if url_passed else 'FAILED'}")
        
        # Dual deployment summary
        print("\n" + "=" * 60)
        print("📊 DUAL DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        firebase_status = results.get('firebase_hosting', {})
        github_status = results.get('github_pages', {})
        
        print(f"🔥 Firebase (PRIMARY):  {'✅ LIVE' if firebase_status.get('passed') else '❌ DOWN'}")
        print(f"📚 GitHub Pages (BACKUP): {'✅ LIVE' if github_status.get('passed') else '❌ DOWN'}")
        
        if firebase_status.get('passed') and github_status.get('passed'):
            print("\n🎊 DUAL DEPLOYMENT: FULLY OPERATIONAL!")
            print("🌐 Both primary and backup sites are live and healthy!")
        elif firebase_status.get('passed'):
            print("\n⚠️ PARTIAL SUCCESS: Primary site operational, backup has issues")
            print("🔥 Firebase hosting is serving traffic correctly")
        elif github_status.get('passed'):
            print("\n⚠️ PARTIAL SUCCESS: Backup site operational, primary has issues") 
            print("📚 GitHub Pages can serve as fallback")
        else:
            print("\n❌ CRITICAL: Both deployments have issues!")
        
        print("\n🎯 Recommended Actions:")
        if all_passed:
            print("  • No action required - all systems operational")
            print("  • Monitor performance metrics")
            print("  • Schedule next verification")
        else:
            print("  • Check failed deployment logs")
            print("  • Verify GitHub Actions status")
            print("  • Test manual deployment")
        
        return all_passed

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    success = verifier.run_full_verification()
    exit(0 if success else 1)
