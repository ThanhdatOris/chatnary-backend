#!/usr/bin/env python3
"""
Cleanup script để dọn dẹp legacy Node.js code và tối ưu hóa project
"""

import os
import shutil
import json
from pathlib import Path

# Legacy Node.js files và directories cần xóa
LEGACY_FILES = [
    'server.js',
    'package.json', 
    'package-lock.json',
    'nodemon.json',
    'meilisearch.exe',
    'start-meilisearch.bat',
    'start.bat',
    'quick-auth-test.js',
    'test-api.js',
    'test-auth.js', 
    'test-connections.js',
    'test-meilisearch.js',
    'test-search.js',
    'upload-and-test.js'
]

LEGACY_DIRS = [
    'node_modules',
    'config',          # Node.js config (không phải app/config)
    'controllers',     # Node.js controllers
    'middleware',      # Node.js middleware  
    'routes',          # Node.js routes
    'services',        # Node.js services (không phải app/services)
    'dumps',
    'venv'             # Python venv (sẽ tái tạo)
]

# Temporary/runtime directories cần dọn
TEMP_DIRS = [
    'meili_data',
    'logs',
    '__pycache__',
    '.pytest_cache'
]

def cleanup_legacy():
    """Dọn dẹp legacy Node.js code"""
    print("🧹 Dọn dẹp legacy Node.js code...")
    
    removed_files = 0
    removed_dirs = 0
    
    # Xóa legacy files
    for file_name in LEGACY_FILES:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"  ✅ Removed file: {file_name}")
                removed_files += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {file_name}: {e}")
    
    # Xóa legacy directories
    for dir_name in LEGACY_DIRS:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  ✅ Removed directory: {dir_name}")
                removed_dirs += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {dir_name}: {e}")
    
    print(f"📊 Cleanup summary: {removed_files} files, {removed_dirs} directories removed")

def cleanup_temp():
    """Dọn dẹp temporary và runtime files"""
    print("🧹 Dọn dẹp temporary files...")
    
    for dir_name in TEMP_DIRS:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name) 
                print(f"  ✅ Cleaned: {dir_name}")
            except Exception as e:
                print(f"  ❌ Failed to clean {dir_name}: {e}")
    
    # Dọn Python cache files
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✅ Cleaned: {cache_dir}")
            except:
                pass
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                try:
                    os.remove(pyc_file)
                    print(f"  ✅ Cleaned: {pyc_file}")
                except:
                    pass

def optimize_docker():
    """Tối ưu hóa Docker configuration"""
    print("🐳 Tối ưu hóa Docker configuration...")
    
    # Tạo .dockerignore để loại trừ files không cần thiết
    dockerignore_content = """
# Legacy Node.js files
server.js
package*.json
nodemon.json
*.js
config/
controllers/
middleware/
routes/
services/
node_modules/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Runtime data
meili_data/
logs/
uploads/
vector_stores/
dumps/

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation
*.md
!README.md
"""
    
    with open('.dockerignore', 'w') as f:
        f.write(dockerignore_content.strip())
    print("  ✅ Created optimized .dockerignore")

def update_gitignore():
    """Cập nhật .gitignore"""
    print("📝 Cập nhật .gitignore...")
    
    gitignore_content = """
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
pip-log.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.pytest_cache/

# Legacy Node.js (cleaned)
node_modules/
package*.json
*.js
config/
controllers/
middleware/
routes/
services/

# Meilisearch files
meilisearch.exe
meili_data/

# Uploads and data
uploads/
vector_stores/
logs/
dumps/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    print("  ✅ Updated .gitignore")

def create_optimized_requirements():
    """Tạo requirements.txt tối ưu"""
    print("📦 Tối ưu requirements.txt...")
    
    # Requirements tối ưu với versions ổn định
    optimized_requirements = """
# Chatnary Python Backend - Optimized Requirements

# FastAPI Core (stable versions)
fastapi>=0.100.0,<0.105.0
uvicorn[standard]>=0.20.0,<0.25.0
python-multipart>=0.0.5

# Authentication & Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
email-validator>=2.0.0

# Database
motor>=3.3.0
pymongo>=4.6.0

# AI & RAG Dependencies (locked for stability)
langchain>=0.1.0,<0.3.0
langchain-community>=0.0.10
langchain-openai>=0.0.5
langchain-google-genai>=1.0.0
openai>=1.3.0
faiss-cpu>=1.7.4
sentence-transformers>=2.2.0
google-generativeai>=0.3.0

# Document Processing
pypdf>=3.17.0

# Configuration & Environment
python-dotenv>=1.0.0
pydantic-settings>=2.0.0

# Utilities
aiofiles>=23.0.0
python-dateutil>=2.8.0
typing-extensions>=4.8.0

# HTTP Client for testing
httpx>=0.24.0

# Development (optional)
pytest>=7.4.0
pytest-asyncio>=0.21.0
""".strip()
    
    with open('requirements.txt', 'w') as f:
        f.write(optimized_requirements)
    print("  ✅ Created optimized requirements.txt")

def main():
    """Main cleanup function"""
    print("🚀 Starting Chatnary Backend Cleanup & Optimization")
    print("=" * 60)
    
    try:
        cleanup_legacy()
        print()
        
        cleanup_temp()
        print()
        
        optimize_docker()
        print()
        
        update_gitignore()
        print()
        
        create_optimized_requirements()
        print()
        
        print("✅ Cleanup và optimization hoàn thành!")
        print()
        print("📋 Next steps:")
        print("1. docker-compose down")
        print("2. docker-compose build --no-cache") 
        print("3. docker-compose up -d")
        print("4. python test_new_backend.py")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    main()

