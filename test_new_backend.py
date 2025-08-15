#!/usr/bin/env python3
"""
Test script for new Chatnary Python Backend
Comprehensive testing of all endpoints and functionality
"""

import asyncio
import httpx
import json
import os
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "9588666@gmail.com",
    "password": "123456",
    "fullName": "Nguyễn Thành Đạt"
}

class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token = None
        self.test_file_id = None
    
    async def test_health_check(self):
        """Test basic health check"""
        print("🔍 Testing health check...")
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['backend']} v{data['version']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        print("🔍 Testing root endpoint...")
        try:
            response = await self.client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint: {data['message']}")
                print(f"   Features: {len(data['features'])} available")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    async def test_user_registration(self):
        """Test user registration"""
        print("🔍 Testing user registration...")
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/auth/register",
                json=TEST_USER
            )
            if response.status_code == 201:
                data = response.json()
                self.token = data["token"]
                print(f"✅ User registration successful: {data['user']['email']}")
                return True
            elif response.status_code == 400 and "đã được sử dụng" in response.json()["detail"]:
                print("ℹ️  User already exists, trying login...")
                return await self.test_user_login()
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    async def test_user_login(self):
        """Test user login"""
        print("🔍 Testing user login...")
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["token"]
                print(f"✅ User login successful: {data['user']['email']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    async def test_protected_endpoint(self):
        """Test protected endpoint (profile)"""
        print("🔍 Testing protected endpoint...")
        if not self.token:
            print("❌ No token available for protected endpoint test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.get(
                f"{BASE_URL}/api/auth/profile",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Protected endpoint works: {data['user']['fullName']}")
                return True
            else:
                print(f"❌ Protected endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
            return False
    
    async def test_file_upload(self):
        """Test file upload functionality"""
        print("🔍 Testing file upload...")
        if not self.token:
            print("❌ No token available for file upload test")
            return False
        
        # Create a test file
        test_content = """
# Test Document for Chatnary

This is a test document for the Chatnary AI system.

## Features
- Document upload and management
- AI-powered chat with documents
- Multi-user support
- Vector similarity search

## Technical Details
The system uses FastAPI with Python for backend processing.
RAG (Retrieval Augmented Generation) enables intelligent document chat.
        """.strip()
        
        test_file_path = "test_document.txt"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                response = await self.client.post(
                    f"{BASE_URL}/api/upload",
                    headers=headers,
                    files=files
                )
            
            # Clean up test file
            os.remove(test_file_path)
            
            if response.status_code == 200:
                data = response.json()
                self.test_file_id = data["file"]["id"]
                print(f"✅ File upload successful: {data['file']['originalName']}")
                return True
            else:
                print(f"❌ File upload failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ File upload error: {e}")
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
            return False
    
    async def test_file_list(self):
        """Test file listing"""
        print("🔍 Testing file listing...")
        if not self.token:
            print("❌ No token available for file list test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.get(
                f"{BASE_URL}/api/files",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                file_count = len(data["data"]["files"])
                print(f"✅ File listing successful: {file_count} files found")
                return True
            else:
                print(f"❌ File listing failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ File listing error: {e}")
            return False
    
    async def test_ai_model_status(self):
        """Test AI model status"""
        print("🔍 Testing AI model status...")
        try:
            response = await self.client.get(f"{BASE_URL}/api/chat/models")
            if response.status_code == 200:
                data = response.json()
                available_models = [model for model, available in data["models"].items() if available]
                print(f"✅ AI models status: {len(available_models)} available ({', '.join(available_models)})")
                return True
            else:
                print(f"❌ AI model status failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ AI model status error: {e}")
            return False
    
    async def test_document_processing(self):
        """Test document processing for AI"""
        print("🔍 Testing document processing...")
        if not self.token or not self.test_file_id:
            print("❌ No token or file available for processing test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.post(
                f"{BASE_URL}/api/process-document/{self.test_file_id}",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Document processing successful: {data['message']}")
                return True
            else:
                print(f"❌ Document processing failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Document processing error: {e}")
            return False
    
    async def test_ai_chat(self):
        """Test AI chat functionality"""
        print("🔍 Testing AI chat...")
        if not self.token:
            print("❌ No token available for chat test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            chat_request = {
                "query": "What is this document about?",
                "model": "gemini",
                "top_k": 3
            }
            
            response = await self.client.post(
                f"{BASE_URL}/api/chat",
                headers=headers,
                json=chat_request
            )
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data["answer"])
                source_count = len(data["sources"])
                processing_time = data["processing_time"]
                print(f"✅ AI chat successful:")
                print(f"   Answer length: {answer_length} chars")
                print(f"   Sources: {source_count}")
                print(f"   Processing time: {processing_time:.2f}s")
                print(f"   Model used: {data['model_used']}")
                return True
            else:
                print(f"❌ AI chat failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ AI chat error: {e}")
            return False
    
    async def test_file_stats(self):
        """Test file statistics"""
        print("🔍 Testing file statistics...")
        try:
            response = await self.client.get(f"{BASE_URL}/api/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data["stats"]
                print(f"✅ File stats: {stats['totalFiles']} total, {stats['indexedFiles']} indexed")
                return True
            else:
                print(f"❌ File stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ File stats error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Chatnary Python Backend Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("User Registration", self.test_user_registration),
            ("Protected Endpoint", self.test_protected_endpoint),
            ("File Upload", self.test_file_upload),
            ("File Listing", self.test_file_list),
            ("AI Model Status", self.test_ai_model_status),
            ("Document Processing", self.test_document_processing),
            ("AI Chat", self.test_ai_chat),
            ("File Statistics", self.test_file_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                result = await test_func()
                if result:
                    passed += 1
                # Small delay between tests
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
        
        print("\n" + "=" * 50)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Check failed tests above.")
        else:
            print("❌ Many tests failed. Check configuration and dependencies.")
        
        await self.client.aclose()
        return passed == total

async def main():
    """Main test function"""
    tester = BackendTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
