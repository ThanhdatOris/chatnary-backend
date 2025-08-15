#!/usr/bin/env python3
"""
Frontend Compatibility Test Suite
Kiểm tra tương thích API giữa Python backend và frontend requirements
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class FrontendCompatibilityTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token = None
        self.test_results = []
    
    def log_test(self, endpoint: str, method: str, expected: bool, actual: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if expected == actual else "❌ FAIL"
        self.test_results.append({
            "endpoint": endpoint,
            "method": method,
            "expected": expected,
            "actual": actual,
            "status": status,
            "details": details
        })
        print(f"{status} {method} {endpoint} - {details}")
    
    async def test_auth_endpoints(self):
        """Test authentication endpoints that frontend expects"""
        print("\n🔐 Testing Authentication Endpoints")
        print("-" * 50)
        
        # Test registration
        try:
            response = await self.client.post(f"{BASE_URL}/api/auth/register", json={
                "email": "frontend-test@chatnary.com",
                "password": "frontend123456",
                "fullName": "Frontend Test User"
            })
            
            if response.status_code == 201:
                data = response.json()
                expected_fields = ["success", "user", "token"]
                has_all_fields = all(field in data for field in expected_fields)
                self.token = data.get("token")
                self.log_test("/api/auth/register", "POST", True, has_all_fields, 
                            f"Status: {response.status_code}, Fields: {list(data.keys())}")
            else:
                # Try login if user exists
                response = await self.client.post(f"{BASE_URL}/api/auth/login", json={
                    "email": "frontend-test@chatnary.com", 
                    "password": "frontend123456"
                })
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("token")
                    self.log_test("/api/auth/register", "POST", True, True, "User exists, login successful")
                else:
                    self.log_test("/api/auth/register", "POST", True, False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("/api/auth/register", "POST", True, False, f"Error: {e}")
        
        # Test login  
        try:
            response = await self.client.post(f"{BASE_URL}/api/auth/login", json={
                "email": "frontend-test@chatnary.com",
                "password": "frontend123456"
            })
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Fields: {list(data.keys())}"
            self.log_test("/api/auth/login", "POST", True, success, details)
        except Exception as e:
            self.log_test("/api/auth/login", "POST", True, False, f"Error: {e}")
        
        # Test profile (protected)
        if self.token:
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = await self.client.get(f"{BASE_URL}/api/auth/profile", headers=headers)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    data = response.json()
                    details += f", User ID: {data.get('user', {}).get('id', 'N/A')}"
                self.log_test("/api/auth/profile", "GET", True, success, details)
            except Exception as e:
                self.log_test("/api/auth/profile", "GET", True, False, f"Error: {e}")
        else:
            self.log_test("/api/auth/profile", "GET", True, False, "No token available")
    
    async def test_file_endpoints(self):
        """Test file management endpoints"""
        print("\n📁 Testing File Management Endpoints")
        print("-" * 50)
        
        if not self.token:
            print("⚠️ Skipping file tests - no authentication token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test file upload
        try:
            test_content = "Frontend compatibility test document content"
            files = {"file": ("frontend-test.txt", test_content, "text/plain")}
            response = await self.client.post(f"{BASE_URL}/api/upload", headers=headers, files=files)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", File ID: {data.get('file', {}).get('id', 'N/A')}"
            self.log_test("/api/upload", "POST", True, success, details)
        except Exception as e:
            self.log_test("/api/upload", "POST", True, False, f"Error: {e}")
        
        # Test file listing
        try:
            response = await self.client.get(f"{BASE_URL}/api/files", headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                file_count = len(data.get('data', {}).get('files', []))
                details += f", Files: {file_count}"
            self.log_test("/api/files", "GET", True, success, details)
        except Exception as e:
            self.log_test("/api/files", "GET", True, False, f"Error: {e}")
        
        # Test file stats
        try:
            response = await self.client.get(f"{BASE_URL}/api/stats")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                total_files = data.get('stats', {}).get('totalFiles', 0)
                details += f", Total files: {total_files}"
            self.log_test("/api/stats", "GET", True, success, details)
        except Exception as e:
            self.log_test("/api/stats", "GET", True, False, f"Error: {e}")
    
    async def test_search_endpoints(self):
        """Test search endpoints"""
        print("\n🔍 Testing Search Endpoints")
        print("-" * 50)
        
        # Test search
        try:
            response = await self.client.get(f"{BASE_URL}/api/search?query=test&limit=10")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                hit_count = data.get('data', {}).get('hitsCount', 0)
                details += f", Hits: {hit_count}"
            self.log_test("/api/search", "GET", True, success, details)
        except Exception as e:
            self.log_test("/api/search", "GET", True, False, f"Error: {e}")
        
        # Test suggestions
        try:
            response = await self.client.get(f"{BASE_URL}/api/suggestions?q=test")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                suggestion_count = len(data.get('suggestions', []))
                details += f", Suggestions: {suggestion_count}"
            self.log_test("/api/suggestions", "GET", True, success, details)
        except Exception as e:
            self.log_test("/api/suggestions", "GET", True, False, f"Error: {e}")
    
    async def test_ai_endpoints(self):
        """Test AI/Chat endpoints"""
        print("\n🤖 Testing AI & Chat Endpoints")
        print("-" * 50)
        
        # Test AI model status
        try:
            response = await self.client.get(f"{BASE_URL}/api/chat/models")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                models = data.get('models', {})
                available_count = sum(1 for available in models.values() if available)
                details += f", Available models: {available_count}"
            self.log_test("/api/chat/models", "GET", True, success, details)
        except Exception as e:
            self.log_test("/api/chat/models", "GET", True, False, f"Error: {e}")
        
        # Test chat endpoint (requires auth)
        if self.token:
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                chat_data = {
                    "query": "What is this document about?",
                    "model": "gemini",
                    "top_k": 3
                }
                response = await self.client.post(f"{BASE_URL}/api/chat", headers=headers, json=chat_data)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    data = response.json()
                    answer_length = len(data.get('answer', ''))
                    details += f", Answer length: {answer_length}"
                self.log_test("/api/chat", "POST", True, success, details)
            except Exception as e:
                self.log_test("/api/chat", "POST", True, False, f"Error: {e}")
        else:
            self.log_test("/api/chat", "POST", True, False, "No token available")
    
    async def test_cors_and_headers(self):
        """Test CORS and headers for frontend compatibility"""
        print("\n🌐 Testing CORS & Headers")
        print("-" * 50)
        
        # Test CORS preflight
        try:
            response = await self.client.options(f"{BASE_URL}/api/auth/login", headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            })
            success = response.status_code in [200, 204]
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            details = f"Status: {response.status_code}, CORS headers: {bool(any(cors_headers.values()))}"
            self.log_test("CORS Preflight", "OPTIONS", True, success, details)
        except Exception as e:
            self.log_test("CORS Preflight", "OPTIONS", True, False, f"Error: {e}")
    
    async def check_api_structure_compatibility(self):
        """Check API response structure compatibility"""
        print("\n📋 Testing API Response Structure")
        print("-" * 50)
        
        # Test standardized response format
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                has_standard_fields = "status" in data
                self.log_test("Standard Response Format", "GET", True, has_standard_fields, 
                            f"Health response structure: {list(data.keys())}")
        except Exception as e:
            self.log_test("Standard Response Format", "GET", True, False, f"Error: {e}")
    
    def generate_compatibility_report(self):
        """Generate frontend compatibility report"""
        print("\n" + "=" * 60)
        print("📊 FRONTEND COMPATIBILITY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["actual"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Overall Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n⚠️ Issues found:")
            for result in self.test_results:
                if not result["actual"]:
                    print(f"   ❌ {result['method']} {result['endpoint']} - {result['details']}")
        
        print(f"\n🎯 Frontend Integration Status:")
        if passed_tests >= total_tests * 0.8:
            print("✅ READY for frontend integration!")
            print("   Most endpoints are working correctly.")
        elif passed_tests >= total_tests * 0.6:
            print("⚠️ PARTIALLY READY")  
            print("   Core endpoints work, some features need attention.")
        else:
            print("❌ NOT READY")
            print("   Major issues need to be resolved first.")
        
        print(f"\n📋 Recommended Actions:")
        print("1. Fix database connection issues if any")
        print("2. Update frontend API endpoints to match backend")
        print("3. Test file upload/download functionality")
        print("4. Implement missing chat features as needed")
        
        return passed_tests / total_tests >= 0.8
    
    async def run_all_tests(self):
        """Run complete frontend compatibility test suite"""
        print("🚀 Starting Frontend Compatibility Tests")
        print("Testing against backend: " + BASE_URL)
        print("=" * 60)
        
        try:
            await self.test_auth_endpoints()
            await self.test_file_endpoints()
            await self.test_search_endpoints()
            await self.test_ai_endpoints()
            await self.test_cors_and_headers()
            await self.check_api_structure_compatibility()
            
            return self.generate_compatibility_report()
            
        finally:
            await self.client.aclose()

async def main():
    """Main test function"""
    tester = FrontendCompatibilityTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
