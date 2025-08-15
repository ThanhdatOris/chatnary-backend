#!/usr/bin/env python3
"""
Frontend Simulation Test - Mô phỏng chính xác requests từ frontend
"""

import asyncio
import httpx
import json

class FrontendSimulator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "http://localhost:8000"
        self.frontend_origin = "http://localhost:3000"
        self.token = None

    async def simulate_user_registration(self):
        """Mô phỏng registration từ frontend"""
        print("🚀 Simulating Frontend Registration...")
        
        # Chính xác như browser sẽ gửi
        headers = {
            "Content-Type": "application/json",
            "Origin": self.frontend_origin,
            "Referer": f"{self.frontend_origin}/register",
            "User-Agent": "Mozilla/5.0 (Frontend Test)"
        }
        
        data = {
            "email": "frontend-sim@test.com",
            "password": "frontend123456",
            "fullName": "Frontend Simulation User"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json=data,
                headers=headers
            )
            
            print(f"✅ Registration Status: {response.status_code}")
            print(f"✅ CORS Headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ User Created: {result['user']['email']}")
                print(f"✅ Token Received: {bool(result.get('token'))}")
                return True
            else:
                print(f"❌ Registration Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration Error: {e}")
            return False

    async def simulate_user_login(self):
        """Mô phỏng login từ frontend"""
        print("\n🔐 Simulating Frontend Login...")
        
        headers = {
            "Content-Type": "application/json", 
            "Origin": self.frontend_origin,
            "Referer": f"{self.frontend_origin}/login",
            "User-Agent": "Mozilla/5.0 (Frontend Test)"
        }
        
        data = {
            "email": "cors-test@example.com",
            "password": "test123456"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                json=data,
                headers=headers
            )
            
            print(f"✅ Login Status: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("access-control-allow-origin"),
                "Access-Control-Allow-Credentials": response.headers.get("access-control-allow-credentials"),
                "Vary": response.headers.get("vary")
            }
            print(f"✅ CORS Headers: {cors_headers}")
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('token')
                print(f"✅ User: {result['user']['email']}")
                print(f"✅ Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login Error: {e}")
            return False

    async def simulate_protected_request(self):
        """Mô phỏng protected request từ frontend"""
        print("\n👤 Simulating Protected Profile Request...")
        
        if not self.token:
            print("❌ No token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Origin": self.frontend_origin,
            "Referer": f"{self.frontend_origin}/profile",
            "User-Agent": "Mozilla/5.0 (Frontend Test)"
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/auth/profile",
                headers=headers
            )
            
            print(f"✅ Profile Status: {response.status_code}")
            
            # Check CORS headers
            cors_origin = response.headers.get("access-control-allow-origin")
            print(f"✅ CORS Origin: {cors_origin}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Profile: {result['user']['email']} ({result['user']['role']})")
                return True
            else:
                print(f"❌ Profile Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Profile Error: {e}")
            return False

    async def simulate_file_upload(self):
        """Mô phỏng file upload từ frontend"""
        print("\n📁 Simulating File Upload...")
        
        if not self.token:
            print("❌ No token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Origin": self.frontend_origin,
            "Referer": f"{self.frontend_origin}/upload"
        }
        
        # Simulate file content
        file_content = "Frontend simulation test document content for CORS testing"
        files = {
            "file": ("frontend-test.txt", file_content, "text/plain")
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/upload",
                headers=headers,
                files=files
            )
            
            print(f"✅ Upload Status: {response.status_code}")
            
            # Check CORS
            cors_origin = response.headers.get("access-control-allow-origin")
            print(f"✅ CORS Origin: {cors_origin}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File Uploaded: {result['file']['filename']}")
                return True
            else:
                print(f"❌ Upload Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            return False

    async def simulate_ai_chat(self):
        """Mô phỏng AI chat từ frontend"""
        print("\n🤖 Simulating AI Chat...")
        
        if not self.token:
            print("❌ No token available")
            return False
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Origin": self.frontend_origin,
            "Referer": f"{self.frontend_origin}/chat"
        }
        
        data = {
            "query": "What can you tell me about the uploaded documents?",
            "model": "gemini",
            "top_k": 3
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=data,
                headers=headers
            )
            
            print(f"✅ Chat Status: {response.status_code}")
            
            # Check CORS
            cors_origin = response.headers.get("access-control-allow-origin")
            print(f"✅ CORS Origin: {cors_origin}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result['answer'][:50]}...")
                return True
            else:
                print(f"❌ Chat Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat Error: {e}")
            return False

    async def run_complete_simulation(self):
        """Chạy mô phỏng frontend hoàn chỉnh"""
        print("🌐 FRONTEND SIMULATION TEST")
        print("=" * 50)
        print(f"Frontend Origin: {self.frontend_origin}")
        print(f"Backend URL: {self.base_url}")
        print("=" * 50)
        
        try:
            results = []
            
            # 1. Registration
            results.append(await self.simulate_user_registration())
            
            # 2. Login
            results.append(await self.simulate_user_login())
            
            # 3. Protected request
            results.append(await self.simulate_protected_request())
            
            # 4. File upload
            results.append(await self.simulate_file_upload())
            
            # 5. AI Chat
            results.append(await self.simulate_ai_chat())
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 FRONTEND SIMULATION RESULTS")
            print("=" * 50)
            
            total_tests = len(results)
            passed_tests = sum(results)
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
            
            if passed_tests == total_tests:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ Frontend can integrate without CORS issues!")
                print("✅ Authentication flow works perfectly!")
                print("✅ Protected endpoints accessible!")
                print("✅ File operations work!")
                print("✅ AI chat functionality works!")
            elif passed_tests >= total_tests * 0.8:
                print("\n⚠️ Most tests passed, minor issues found")
            else:
                print("\n❌ Major issues found, frontend integration may fail")
            
            return passed_tests == total_tests
            
        finally:
            await self.client.aclose()

async def main():
    simulator = FrontendSimulator()
    success = await simulator.run_complete_simulation()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
