#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

async def test_connection():
    """Test MongoDB connection"""
    try:
        # Load .env file explicitly for testing
        from dotenv import load_dotenv
        load_dotenv()
        
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in environment")
            print("💡 Make sure you have .env file with MONGODB_URI variable")
            return False
        
        print(f"🔄 Testing connection to MongoDB Atlas...")
        print(f"🔗 URI: {mongodb_uri[:50]}...")
        
        # Try different connection configurations for Atlas
        connection_options = {
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "retryWrites": True,
            "w": "majority"
        }
        
        # Don't set TLS options for Atlas - let it handle automatically
        client = AsyncIOMotorClient(mongodb_uri, **connection_options)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client['chatnary']
        collections = await db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"⚠️ Connection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
