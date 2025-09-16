#!/usr/bin/env python3
"""
Debug MongoDB Atlas connection issues
"""

import asyncio
import os
import ssl
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

async def debug_connection():
    """Debug different connection approaches"""
    
    # Load environment
    load_dotenv()
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found")
        return
    
    print(f"🔗 URI: {mongodb_uri[:50]}...")
    
    # Test 1: Minimal connection (let Atlas handle everything)
    print("\n=== Test 1: Minimal Connection ===")
    try:
        client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        await client.admin.command('ping')
        print("✅ Minimal connection successful!")
        client.close()
    except Exception as e:
        print(f"❌ Minimal connection failed: {e}")
    
    # Test 2: With explicit TLS settings
    print("\n=== Test 2: Explicit TLS Settings ===")
    try:
        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=15000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsInsecure=True
        )
        await client.admin.command('ping')
        print("✅ TLS connection successful!")
        client.close()
    except Exception as e:
        print(f"❌ TLS connection failed: {e}")
    
    # Test 3: Check SSL context
    print("\n=== Test 3: SSL Context Info ===")
    try:
        import ssl
        print(f"SSL version: {ssl.OPENSSL_VERSION}")
        print(f"SSL ciphers available: {len(ssl.get_default_context().get_ciphers())}")
        
        # Try with custom SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,
            ssl_context=ssl_context
        )
        await client.admin.command('ping')
        print("✅ Custom SSL context successful!")
        client.close()
    except Exception as e:
        print(f"❌ SSL context failed: {e}")
    
    # Test 4: Check DNS resolution
    print("\n=== Test 4: DNS Resolution ===")
    try:
        import socket
        if "mongodb+srv" in mongodb_uri:
            # Extract hostname from SRV URI
            hostname = mongodb_uri.split("://")[1].split("/")[0].split("@")[-1]
            print(f"Resolving: {hostname}")
            ip = socket.gethostbyname(hostname)
            print(f"✅ DNS resolution successful: {ip}")
        else:
            print("Not an SRV URI, skipping DNS test")
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_connection())

