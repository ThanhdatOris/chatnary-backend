#!/usr/bin/env python3
"""
Test CORS issues khi đăng nhập - Simulate frontend requests
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
FRONTEND_ORIGIN = "http://localhost:3000"

class CORSLoginTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []

    def log_result(self, test_name: str, success: bool, details: str):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name} - {details}")

    async def test_cors_preflight_login(self):
        """Test CORS preflight cho login endpoint"""
        print("\n🌐 Testing CORS Preflight for Login")
        print("-" * 50)
        
        try:
            # CORS Preflight request for login
            response = await self.client.options(
                f"{BASE_URL}/api/auth/login",
                headers={
                    "Origin": FRONTEND_ORIGIN,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type,authorization"
                }
            )
            
            success = response.status_code in [200, 204]
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            cors_methods = response.headers.get("Access-Control-Allow-Methods")
            cors_headers = response.headers.get("Access-Control-Allow-Headers")
            
            details = f"Status: {response.status_code}, Origin: {cors_origin}, Methods: {cors_methods}"
            
            self.log_result("CORS Preflight Login", success, details)
            return success
            
        except Exception as e:
            self.log_result("CORS Preflight Login", False, f"Error: {e}")
            return False

    async def test_cors_actual_login(self):
        """Test actual login request với CORS headers"""
        print("\n🔐 Testing Actual Login with CORS")
        print("-" * 50)
        
        try:
            # Actual login request with Origin header
            response = await self.client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": "simple@test.com",
                    "password": "test123456"
                },
                headers={
                    "Origin": FRONTEND_ORIGIN,
                    "Content-Type": "application/json"
                }
            )
            
            success = response.status_code == 200
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
            
            if success:
                data = response.json()
                has_token = "token" in data
                details = f"Status: {response.status_code}, CORS Origin: {cors_origin}, Has Token: {has_token}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
            
            self.log_result("Login with CORS", success, details)
            return response if success else None
            
        except Exception as e:
            self.log_result("Login with CORS", False, f"Error: {e}")
            return None

    async def test_cors_profile_access(self, login_response):
        """Test protected endpoint access với CORS"""
        print("\n👤 Testing Protected Profile Access with CORS")
        print("-" * 50)
        
        if not login_response:
            self.log_result("Profile Access with CORS", False, "No login token available")
            return
            
        try:
            data = login_response.json()
            token = data.get("token")
            
            if not token:
                self.log_result("Profile Access with CORS", False, "No token in login response")
                return
            
            # Profile request with CORS headers
            response = await self.client.get(
                f"{BASE_URL}/api/auth/profile",
                headers={
                    "Origin": FRONTEND_ORIGIN,
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            success = response.status_code == 200
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            
            if success:
                profile_data = response.json()
                user_email = profile_data.get("user", {}).get("email", "N/A")
                details = f"Status: {response.status_code}, CORS Origin: {cors_origin}, User: {user_email}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
            
            self.log_result("Profile Access with CORS", success, details)
            
        except Exception as e:
            self.log_result("Profile Access with CORS", False, f"Error: {e}")

    async def test_cors_registration(self):
        """Test registration với CORS"""
        print("\n📝 Testing Registration with CORS")
        print("-" * 50)
        
        try:
            # Registration request with CORS headers
            response = await self.client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": f"corstest_{int(asyncio.get_event_loop().time())}@test.com",
                    "password": "corstest123456",
                    "fullName": "CORS Test User"
                },
                headers={
                    "Origin": FRONTEND_ORIGIN,
                    "Content-Type": "application/json"
                }
            )
            
            success = response.status_code == 201
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            
            if success:
                data = response.json()
                has_token = "token" in data
                user_email = data.get("user", {}).get("email", "N/A")
                details = f"Status: {response.status_code}, CORS Origin: {cors_origin}, User: {user_email}, Has Token: {has_token}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
            
            self.log_result("Registration with CORS", success, details)
            
        except Exception as e:
            self.log_result("Registration with CORS", False, f"Error: {e}")

    async def test_cors_different_origins(self):
        """Test CORS với different origins"""
        print("\n🌍 Testing CORS with Different Origins")
        print("-" * 50)
        
        origins_to_test = [
            "http://localhost:3000",    # Frontend dev
            "http://localhost:3001",    # Alternative port
            "https://chatnary.com",     # Production domain (example)
            "http://127.0.0.1:3000",    # Different localhost format
            "null"                      # File:// origin
        ]
        
        for origin in origins_to_test:
            try:
                response = await self.client.options(
                    f"{BASE_URL}/api/auth/login",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type"
                    }
                )
                
                success = response.status_code in [200, 204]
                cors_origin = response.headers.get("Access-Control-Allow-Origin")
                allowed = cors_origin == origin or cors_origin == "*"
                
                details = f"Origin: {origin}, Allowed Origin: {cors_origin}, Status: {response.status_code}"
                test_name = f"CORS Origin {origin}"
                
                self.log_result(test_name, success and allowed, details)
                
            except Exception as e:
                self.log_result(f"CORS Origin {origin}", False, f"Error: {e}")

    async def test_cors_headers_configuration(self):
        """Test CORS headers configuration"""
        print("\n⚙️ Testing CORS Headers Configuration")
        print("-" * 50)
        
        try:
            response = await self.client.get(f"{BASE_URL}/health", headers={"Origin": FRONTEND_ORIGIN})
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
                "Access-Control-Max-Age": response.headers.get("Access-Control-Max-Age")
            }
            
            present_headers = {k: v for k, v in cors_headers.items() if v is not None}
            
            details = f"CORS Headers: {present_headers}"
            success = len(present_headers) > 0
            
            self.log_result("CORS Headers Configuration", success, details)
            
        except Exception as e:
            self.log_result("CORS Headers Configuration", False, f"Error: {e}")

    def generate_cors_report(self):
        """Generate CORS analysis report"""
        print("\n" + "=" * 60)
        print("📊 CORS LOGIN COMPATIBILITY REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Overall CORS Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n⚠️ CORS Issues Found:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']} - {result['details']}")
        
        print(f"\n🎯 Frontend Integration Status:")
        if passed_tests >= total_tests * 0.8:
            print("✅ CORS is working correctly for login!")
            print("   Frontend should be able to authenticate users.")
        elif passed_tests >= total_tests * 0.6:
            print("⚠️ CORS has some issues")  
            print("   Basic functionality works but some edge cases fail.")
        else:
            print("❌ CORS is not properly configured")
            print("   Frontend will have authentication issues.")
        
        print(f"\n📋 Recommendations:")
        if failed_tests > 0:
            print("1. Check CORS middleware configuration in FastAPI")
            print("2. Verify allowed origins include frontend URL")
            print("3. Ensure credentials are allowed if needed")
            print("4. Test with exact frontend origin")
        else:
            print("1. CORS configuration is working correctly")
            print("2. Frontend can proceed with authentication")
            print("3. All login flows should work properly")
        
        return passed_tests / total_tests >= 0.8

    async def run_all_cors_tests(self):
        """Run complete CORS test suite for login"""
        print("🚀 Starting CORS Login Tests")
        print("Testing CORS for authentication endpoints")
        print("=" * 60)
        
        try:
            # Test CORS preflight
            await self.test_cors_preflight_login()
            
            # Test actual login with CORS
            login_response = await self.test_cors_actual_login()
            
            # Test protected endpoint access
            await self.test_cors_profile_access(login_response)
            
            # Test registration
            await self.test_cors_registration()
            
            # Test different origins
            await self.test_cors_different_origins()
            
            # Test headers configuration
            await self.test_cors_headers_configuration()
            
            return self.generate_cors_report()
            
        finally:
            await self.client.aclose()

async def main():
    """Main CORS test function"""
    tester = CORSLoginTester()
    success = await tester.run_all_cors_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
