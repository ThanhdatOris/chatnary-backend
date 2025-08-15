#!/usr/bin/env python3
"""
Health Check Script for Chatnary Backend
Kiểm tra sức khỏe hệ thống production
"""

import asyncio
import httpx
import sys
from typing import Dict, Any

class HealthChecker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None
    
    async def check_basic_endpoints(self) -> Dict[str, Any]:
        """Kiểm tra các endpoints cơ bản"""
        results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Health check
            try:
                response = await client.get(f"{self.base_url}/health")
                results["health"] = {
                    "status": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0,
                    "data": response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                results["health"] = {"status": False, "error": str(e)}
            
            # API docs
            try:
                response = await client.get(f"{self.base_url}/docs")
                results["docs"] = {"status": response.status_code == 200}
            except Exception as e:
                results["docs"] = {"status": False, "error": str(e)}
            
            # AI models
            try:
                response = await client.get(f"{self.base_url}/api/chat/models")
                results["ai_models"] = {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                results["ai_models"] = {"status": False, "error": str(e)}
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """In kết quả kiểm tra"""
        print("🏥 CHATNARY BACKEND HEALTH CHECK")
        print("=" * 50)
        
        total_checks = len(results)
        passed_checks = sum(1 for result in results.values() if result.get("status", False))
        
        for endpoint, result in results.items():
            status = "✅ HEALTHY" if result.get("status", False) else "❌ UNHEALTHY"
            print(f"{status} {endpoint.upper()}")
            
            if result.get("data"):
                if endpoint == "health":
                    data = result["data"]
                    print(f"   Version: {data.get('version', 'Unknown')}")
                    print(f"   Backend: {data.get('backend', 'Unknown')}")
                    print(f"   AI: {'Integrated' if data.get('ai_integrated') else 'Not Available'}")
                elif endpoint == "ai_models":
                    data = result["data"]
                    models = data.get("models", {})
                    available = [model for model, status in models.items() if status]
                    print(f"   Available Models: {', '.join(available) if available else 'None'}")
            
            if result.get("error"):
                print(f"   Error: {result['error']}")
        
        print(f"\n📊 Overall Health: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
        
        if passed_checks == total_checks:
            print("🎉 ALL SYSTEMS OPERATIONAL!")
            return True
        elif passed_checks >= total_checks * 0.8:
            print("⚠️ MOSTLY OPERATIONAL - Minor issues detected")
            return True
        else:
            print("❌ CRITICAL ISSUES - System may not function properly")
            return False

async def main():
    """Main health check function"""
    checker = HealthChecker()
    
    print("Starting health check...")
    results = await checker.check_basic_endpoints()
    
    success = checker.print_results(results)
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)
