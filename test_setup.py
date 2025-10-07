#!/usr/bin/env python3
"""
Test script to verify the search engine setup and API connectivity.
Run this script after setting up your environment variables to ensure everything works.
"""

import os
import sys
from datetime import datetime

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = {
        'DATAFORSEO_LOGIN': 'DataForSEO API username',
        'DATAFORSEO_PASSWORD': 'DataForSEO API password', 
        'GOOGLE_CLOUD_PROJECT_ID': 'Google Cloud project ID',
        'GOOGLE_APPLICATION_CREDENTIALS': 'Path to Google service account JSON'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"  ❌ {var} - {description}")
            missing_vars.append(var)
        else:
            print(f"  ✅ {var} - Set")
    
    if missing_vars:
        print(f"\n❌ Missing {len(missing_vars)} required environment variables")
        print("Please set these in your .env file or environment")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_dependencies():
    """Test if all required Python packages are installed"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'requests',
        'beautifulsoup4',
        'lxml',
        'google.cloud.discoveryengine',
        'python-dotenv',
        'pydantic',
        'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'google.cloud.discoveryengine':
                import google.cloud.discoveryengine_v1
            else:
                __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages")
        print("Install them with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies are installed")
        return True

def test_dataforseo_connection():
    """Test DataForSEO API connectivity"""
    print("\n🌐 Testing DataForSEO API...")
    
    try:
        from dataforseo_client import DataForSEOClient
        client = DataForSEOClient()
        
        if not client.login or not client.password:
            print("  ❌ DataForSEO credentials not configured")
            return False
        
        print("  ✅ DataForSEO client initialized")
        print("  ℹ️  To fully test, run a search query")
        return True
        
    except Exception as e:
        print(f"  ❌ DataForSEO error: {e}")
        return False

def test_google_ranking_connection():
    """Test Google Ranking API connectivity"""
    print("\n🤖 Testing Google Ranking API...")
    
    try:
        from google_ranking_client import GoogleRankingClient
        client = GoogleRankingClient()
        
        if not client.project_id:
            print("  ❌ Google Cloud project ID not configured")
            return False
        
        if not client.client:
            print("  ❌ Google Cloud client not initialized")
            return False
            
        # Try to test the connection
        connection_ok = client.test_connection()
        if connection_ok:
            print("  ✅ Google Ranking API connected successfully")
            return True
        else:
            print("  ❌ Google Ranking API connection failed")
            print("  ℹ️  Check your Google Cloud setup and credentials")
            return False
            
    except Exception as e:
        print(f"  ❌ Google Ranking API error: {e}")
        return False

def test_web_crawler():
    """Test web crawler functionality"""
    print("\n🕷️  Testing Web Crawler...")
    
    try:
        from web_crawler import WebCrawler
        crawler = WebCrawler()
        
        # Test with a simple URL
        test_urls = ['https://httpbin.org/html']
        results = crawler.crawl_urls_sync(test_urls)
        
        if results and len(results) > 0:
            result = results[0]
            if result.get('status') == 'success':
                print("  ✅ Web crawler working correctly")
                return True
            else:
                print(f"  ⚠️  Web crawler test had issues: {result.get('status')}")
                return False
        else:
            print("  ❌ Web crawler returned no results")
            return False
            
    except Exception as e:
        print(f"  ❌ Web crawler error: {e}")
        return False

def test_search_engine():
    """Test the complete search engine"""
    print("\n🔍 Testing Complete Search Engine...")
    
    try:
        from search_engine import SearchEngine
        engine = SearchEngine()
        
        # Test service status
        status = engine.test_all_services()
        print(f"  Service Status: {status}")
        
        if all(status.values()):
            print("  ✅ All services operational")
            return True
        else:
            failed_services = [name for name, working in status.items() if not working]
            print(f"  ⚠️  Some services not working: {failed_services}")
            return False
            
    except Exception as e:
        print(f"  ❌ Search engine error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Advanced Search Engine - Setup Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Dependencies", test_dependencies),
        ("DataForSEO API", test_dataforseo_connection),
        ("Google Ranking API", test_google_ranking_connection),
        ("Web Crawler", test_web_crawler),
        ("Search Engine", test_search_engine)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your search engine is ready to use.")
        print("Run 'python main.py' to start the server.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        print("Check the README.md for setup instructions.")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed, skipping .env file loading")
    
    success = main()
    sys.exit(0 if success else 1) 