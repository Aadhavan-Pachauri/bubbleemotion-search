# AI Search Engine with Python Execution API

A comprehensive Flask application that combines AI-powered search with emotion classification and secure Python code execution, deployed on Koyeb's serverless platform.

## 🚀 Features

- **AI Search Engine**: DuckDuckGo integration with advanced bot detection bypass
- **Emotion Classification**: Psychological analysis of text with DistilBERT fallback
- **Python Execution API**: Secure sandboxed Python code execution
- **Web UI**: Interactive interface for search and classification
- **Serverless Deployment**: Auto-scaling on Koyeb with global edge locations

## 🔧 API Endpoints

### Search API
```bash
GET /search?q=<query>
```
Returns search results with emotion classification and metadata.

### Classification API
```bash
GET /classify?text=<text>
```
Analyzes text for emotional content and psychological patterns.

### Python Execution API
```bash
POST /execute
Content-Type: application/json

{
  "code": "print('Hello World')\nprint(2 + 2)"
}
```

**Response:**
```json
{
  "execution_id": "abc123",
  "output": "Hello World\n4",
  "error": "",
  "execution_time": 0.015,
  "files": {},
  "success": true,
  "return_code": 0
}
```

### System Status
```bash
GET /status
GET /health
```

### Web Interface
```bash
GET /test
```

## 🛡️ Security Features

- **Pattern Blocking**: Prevents dangerous imports and operations
- **Resource Limits**: 30-second execution timeout, 256MB memory limit
- **Sandboxed Execution**: Isolated temporary directory environment
- **Input Validation**: Comprehensive security filtering

**Blocked Patterns:**
- `import os`, `import subprocess`, `import sys`
- `eval()`, `exec()`, `compile()`
- `open()`, `file()`, `input()`
- Network operations, system commands

## 🚀 Quick Start (Local)

1. **Clone and Install**
```bash
git clone <your-repo>
cd ai-search-engine
pip install -r requirements.txt
```

2. **Run Locally**
```bash
python index.py
```

3. **Test APIs**
```bash
# Search
curl "http://localhost:5001/search?q=python tutorials"

# Classification
curl "http://localhost:5001/classify?text=I love this!"

# Python Execution
curl -X POST http://localhost:5001/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")\nprint(2 + 2)"}'
```

## 🌐 Koyeb Deployment

### Prerequisites
- [Koyeb CLI](https://github.com/koyeb/koyeb-cli) installed
- GitHub repository with your code
- Koyeb account

### One-Command Deployment
```bash
./deploy_koyeb.sh
```

### Manual Deployment
```bash
# Login to Koyeb
koyeb login

# Create app
koyeb app create ai-search-engine

# Deploy service
koyeb service create ai-search-engine/service \
  --app ai-search-engine \
  --git github.com/your-username/your-repo \
  --git-branch main \
  --port 5001:5001 \
  --env PORT=5001 \
  --env FLASK_ENV=production \
  --env PYTHONUNBUFFERED=1 \
  --env KOYEB_DEPLOYMENT=true \
  --instance-type free \
  --health-check-path /health
```

### Environment Variables
```bash
PORT=5001                    # Server port
FLASK_ENV=production         # Production mode
PYTHONUNBUFFERED=1          # Disable Python output buffering
KOYEB_DEPLOYMENT=true       # Enable production settings
```

## 🌍 Global Deployment

The app deploys to 13 global regions:
- **Americas**: Oregon, NYC, São Paulo
- **Europe**: Paris, Frankfurt, London, Sweden, Warsaw
- **Asia**: Singapore, Tokyo, Mumbai, Sydney

## 📊 Scaling Configuration

- **Auto-scaling**: 1-10 instances based on CPU/memory usage
- **Target utilization**: 70% CPU, 80% memory
- **Health checks**: 30s interval, 10s timeout
- **Grace period**: 30s startup time

## 🧪 Testing Examples

### Basic Python Execution
```bash
curl -X POST https://ai-search-engine-your-username.koyeb.app/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "for i in range(5):\n    print(f\"Number: {i}\")"}'
```

### Mathematical Calculations
```bash
curl -X POST https://ai-search-engine-your-username.koyeb.app/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "import math\nprint(f\"Pi: {math.pi}\")\nprint(f\"Square root of 16: {math.sqrt(16)}\")"}'
```

### Data Processing
```bash
curl -X POST https://ai-search-engine-your-username.koyeb.app/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "data = [1, 2, 3, 4, 5]\nprint(f\"Sum: {sum(data)}\")\nprint(f\"Average: {sum(data)/len(data)}\")\nprint(f\"Max: {max(data)}\")"}'
```

## 🔒 Security Notice

This API executes Python code in a sandboxed environment. While security measures are in place:

- **Do not** expose sensitive data or credentials
- **Review** code before execution in production
- **Monitor** usage and implement rate limiting if needed
- **Consider** additional security layers for production use

## 📈 Monitoring

Monitor your deployment at:
- **Koyeb Dashboard**: https://app.koyeb.com/apps/ai-search-engine
- **Logs**: Available in Koyeb console
- **Metrics**: CPU, memory, request tracking

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for conflicting dependencies
   - Verify Dockerfile builds locally: `docker build -t test .`

2. **Deployment Issues**
   - Ensure GitHub repository is public or Koyeb has access
   - Check environment variables are set correctly

3. **Runtime Errors**
   - Review logs in Koyeb dashboard
   - Test locally before deployment

### Local Development
```bash
# Run with debug mode
python index.py

# Test all endpoints
curl http://localhost:5001/health
curl http://localhost:5001/status
```

## 📚 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Koyeb Edge    │    │   Flask App     │    │   External APIs │
│   (Global CDN)  │────│  (Python API)   │────│  (DuckDuckGo)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ├─ Search Engine (Bot Bypass)
                              ├─ Emotion Classifier (DistilBERT)
                              ├─ Python Execution (Sandboxed)
                              └─ Web UI (Interactive)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs via GitHub issues
- **Documentation**: Check Koyeb docs for deployment help
- **Community**: Koyeb Discord community for support