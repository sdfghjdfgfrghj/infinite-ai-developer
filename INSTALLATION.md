# 🚀 Installation Guide - Infinite AI Developer

## Quick Start (Recommended)

### 1. Prerequisites
- **Python 3.11+** (required)
- **Git** (for cloning)
- **Local LLM** (Ollama with 30B+ model recommended)

### 2. Install Ollama (if not already installed)
```bash
# On Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows
# Download from https://ollama.ai/download
```

### 3. Download a Model
```bash
# Recommended: 30B parameter model for best results
ollama pull qwen2.5-coder:32b

# Alternative: Smaller model for testing
ollama pull qwen2.5-coder:14b
```

### 4. Clone and Install
```bash
git clone https://github.com/sdfghjdfgfrghj/infinite-ai-developer.git
cd infinite-ai-developer
pip install -r requirements.txt
```

### 5. Configure
Edit `orchestrator/policies.yaml`:
```yaml
model:
  host: "http://localhost:11434"  # Your Ollama endpoint
  name: "qwen2.5-coder:32b"       # Your model name
  timeout: 300

infinite:
  max_iterations: 1000
  max_debug_cycles: 50
  test_everything: true
```

### 6. Test Installation
```bash
# Quick test
python3 main_infinite.py test --simple

# Build your first app
python3 main_infinite.py build "Create a simple calculator with error handling"
```

## Alternative Installation Methods

### Method 1: Pip Install (Coming Soon)
```bash
pip install infinite-ai-developer
infinite-ai build "Create a task manager"
```

### Method 2: Docker (Coming Soon)
```bash
docker run -it infinite-ai-developer build "Create a web app"
```

### Method 3: Development Setup
```bash
git clone https://github.com/sdfghjdfgfrghj/infinite-ai-developer.git
cd infinite-ai-developer
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Install in development mode
pip install -e .
```

## Configuration Options

### Model Configuration
```yaml
model:
  host: "http://localhost:11434"     # Ollama endpoint
  name: "qwen2.5-coder:32b"          # Model name
  timeout: 300                       # Request timeout in seconds
  retry_attempts: 3                  # Number of retries on failure
```

### Iteration Settings
```yaml
infinite:
  max_iterations: 1000               # Maximum total iterations
  max_debug_cycles: 50               # Maximum debug attempts per issue
  test_everything: true              # Run tests after every phase
  strict_verification: true          # Require 90%+ confidence for completion
```

### Quality Standards
```yaml
quality:
  min_test_coverage: 80              # Minimum test coverage percentage
  max_complexity: 10                 # Maximum cyclomatic complexity
  require_docs: true                 # Require documentation
  require_error_handling: true       # Require robust error handling
```

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'git'"
```bash
pip install gitpython
```

#### 2. "Connection refused to Ollama"
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### 3. "Model not found"
```bash
# List available models
ollama list

# Pull the required model
ollama pull qwen2.5-coder:32b
```

#### 4. Permission errors on Windows/WSL
```bash
# Fix git permissions
git config --global --add safe.directory /path/to/infinite-ai-developer
```

#### 5. "Rich not available" fallback
```bash
pip install rich>=13.0.0
```

### Performance Tips

#### For Better Performance:
- Use **30B+ parameter models** for best results
- Ensure **16GB+ RAM** for large models
- Use **SSD storage** for faster file operations
- **GPU acceleration** if available (CUDA/Metal)

#### For Resource-Constrained Systems:
- Use smaller models like `qwen2.5-coder:14b`
- Reduce `max_iterations` to 100-500
- Set `test_everything: false` for faster iterations

## Verification

### Test Your Installation
```bash
# 1. Check Python version
python3 --version  # Should be 3.11+

# 2. Check Ollama connection
curl http://localhost:11434/api/tags

# 3. Test the system
python3 main_infinite.py test --simple

# 4. Build a real project
python3 main_infinite.py build "Create a todo list CLI app"
```

### Expected Output
```
♾️ Starting infinite autonomous development...
📝 Requirements: Create a todo list CLI app
📁 Project: todo_list_cli_20241201_143022
🔄 Max iterations: 1000

🤖 AUTONOMOUS AI DEVELOPER
✨ FEATURES:
🧠 Uses your local 30B model (unlimited iterations!)
🏗️ Real AI architects that design software
💻 AI coders that write production-ready code
...
```

## Next Steps

Once installed:
1. **Read the [README.md](README.md)** for usage examples
2. **Check the [ROADMAP.md](ROADMAP.md)** for upcoming features
3. **See [CONTRIBUTING.md](CONTRIBUTING.md)** to contribute
4. **Join our community** for support and discussions

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/sdfghjdfgfrghj/infinite-ai-developer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sdfghjdfgfrghj/infinite-ai-developer/discussions)
- 📧 **Email**: contributors@infinite-ai-developer.com

---

**Ready to build amazing applications with infinite AI iterations?** 🚀