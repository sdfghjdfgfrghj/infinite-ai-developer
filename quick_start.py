#!/usr/bin/env python3
"""
🚀 Quick Start Script for Infinite AI Developer
Helps new users get started quickly with proper setup verification
"""

import sys
import subprocess
import json
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.11+")
        return False

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected - {len(models)} models available")
            return True, models
        else:
            print("❌ Ollama not responding properly")
            return False, []
    except requests.exceptions.RequestException:
        print("❌ Ollama not running or not accessible at http://localhost:11434")
        print("💡 Start Ollama with: ollama serve")
        return False, []

def check_required_model():
    """Check if a suitable model is available"""
    connected, models = check_ollama_connection()
    if not connected:
        return False
    
    suitable_models = []
    for model in models:
        name = model.get("name", "")
        if any(keyword in name.lower() for keyword in ["coder", "code", "qwen", "deepseek"]):
            suitable_models.append(name)
    
    if suitable_models:
        print(f"✅ Suitable coding models found: {', '.join(suitable_models[:3])}")
        return True
    else:
        print("❌ No suitable coding models found")
        print("💡 Install a coding model with: ollama pull qwen2.5-coder:14b")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "rich", "pyyaml", "gitpython", "asyncio-mqtt", 
        "dataclasses-json", "fastapi", "uvicorn", "requests", "pytest"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} - installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - missing")
    
    if missing:
        print(f"\n💡 Install missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def run_quick_test():
    """Run a quick test to verify everything works"""
    print("\n🧪 Running quick system test...")
    
    try:
        # Try importing main components
        sys.path.append(str(Path(__file__).parent))
        from ui.beautiful_cli import beautiful_cli
        print("✅ Beautiful CLI - imported successfully")
        
        # Test basic functionality
        beautiful_cli.show_banner()
        print("✅ Beautiful CLI - banner displayed")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main quick start verification"""
    print("🚀 Infinite AI Developer - Quick Start Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Ollama Connection", lambda: check_ollama_connection()[0]),
        ("Coding Model", check_required_model),
        ("Dependencies", check_dependencies),
        ("System Test", run_quick_test)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name} check failed")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! You're ready to use Infinite AI Developer!")
        print("\n🚀 Try your first build:")
        print("python3 main_infinite.py build \"Create a simple calculator with error handling\"")
        
        print("\n📚 Next steps:")
        print("1. Read README.md for detailed usage")
        print("2. Check INSTALLATION.md for advanced setup")
        print("3. See ROADMAP.md for upcoming features")
        
    else:
        print(f"\n⚠️ {total - passed} issues need to be resolved before using the system.")
        print("\n🔧 Common fixes:")
        print("1. Install Python 3.11+: https://python.org/downloads")
        print("2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Pull a model: ollama pull qwen2.5-coder:14b")
        
        print("\n📖 See INSTALLATION.md for detailed troubleshooting")

if __name__ == "__main__":
    main()