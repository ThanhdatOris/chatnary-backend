#!/usr/bin/env python3
"""
Simple test để kiểm tra database connection và basic endpoints
"""

import asyncio
import httpx

async def test_basic():
    async with httpx.AsyncClient() as client:
        # Test health
        print("Testing health...")
        response = await client.get("http://localhost:8000/health")
        print(f"Health: {response.status_code} - {response.text}")
        
        # Test root
        print("\nTesting root...")
        response = await client.get("http://localhost:8000/")
        print(f"Root: {response.status_code} - {response.json()}")
        
        # Test models  
        print("\nTesting AI models...")
        response = await client.get("http://localhost:8000/api/chat/models")
        print(f"Models: {response.status_code} - {response.json()}")
        
        # Test register (database required)
        print("\nTesting registration...")
        try:
            response = await client.post("http://localhost:8000/api/auth/register", json={
                "email": "simple@test.com",
                "password": "test123456", 
                "fullName": "Simple Test"
            })
            print(f"Register: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
            else:
                print(f"Success: {response.json()}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic())
