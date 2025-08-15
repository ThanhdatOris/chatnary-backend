#!/usr/bin/env python3
"""
Setup script for Chatnary Python Backend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run shell command with error handling"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")

def setup_virtual_environment():
    """Setup Python virtual environment"""
    if os.path.exists("venv"):
        print("📁 Virtual environment already exists")
        return
    
    run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    # Activate virtual environment and install
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:  # Linux/Mac
        pip_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    run_command(pip_cmd, "Installing Python dependencies")

def setup_environment_file():
    """Setup environment file"""
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from env.example")
            print("⚠️  Please update .env file with your API keys")
        else:
            print("⚠️  No env.example file found")

def create_directories():
    """Create necessary directories"""
    dirs = ["uploads", "vector_stores", "logs"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"📁 Created {dir_name}/ directory")

def show_next_steps():
    """Show next steps to user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys:")
    print("   - OPENAI_API_KEY (optional)")
    print("   - GEMINI_API_KEY (optional)")
    print("   - MONGODB_URI (if using external MongoDB)")
    print("\n2. Start the services:")
    print("   Option A - Docker (recommended):")
    print("     docker-compose up -d")
    print("\n   Option B - Local development:")
    print("     # Start MongoDB and Meilisearch separately")
    print("     # Then run:")
    if os.name == 'nt':  # Windows
        print("     venv\\Scripts\\python run.py")
    else:  # Linux/Mac
        print("     source venv/bin/activate && python run.py")
    print("\n3. Access the API:")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    print("   - Upload endpoint: http://localhost:8000/api/upload")
    print("   - Chat endpoint: http://localhost:8000/api/chat")

def main():
    """Main setup function"""
    print("🚀 Setting up Chatnary Python Backend...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Setup virtual environment (optional for Docker)
    if "--docker" not in sys.argv:
        setup_virtual_environment()
        install_dependencies()
    
    # Setup environment and directories
    setup_environment_file()
    create_directories()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
