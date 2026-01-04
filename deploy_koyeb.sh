#!/bin/bash
# Koyeb Deployment Script for AI Search Engine with Python Execution

echo "🚀 Deploying AI Search Engine to Koyeb..."

# Check if koyeb CLI is installed
if ! command -v koyeb &> /dev/null; then
    echo "❌ Koyeb CLI not found. Please install it first:"
    echo "   curl https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_$(uname -s)_$(uname -m).tar.gz | tar -xz"
    echo "   sudo mv koyeb /usr/local/bin/"
    exit 1
fi

# Check if user is logged in
if ! koyeb account get &> /dev/null; then
    echo "❌ Not logged in to Koyeb. Please run: koyeb login"
    exit 1
fi

# Create app if it doesn't exist
echo "📦 Creating/updating Koyeb app..."
koyeb app create ai-search-engine --docker docker.io/library/python:3.10-slim || true

# Deploy the service
echo "🐳 Building and deploying service..."
koyeb service create ai-search-engine/service \
    --app ai-search-engine \
    --docker docker.io/library/python:3.10-slim \
    --docker-command "python index.py" \
    --port 5001:5001 \
    --env PORT=5001 \
    --env FLASK_ENV=production \
    --env PYTHONUNBUFFERED=1 \
    --env KOYEB_DEPLOYMENT=true \
    --git github.com/your-username/your-repo \
    --git-branch main \
    --instance-type free \
    --regions was,fra,sin,par,lon,oregon,nyc,tokyo,sydney,saopaulo,mumbai,sweden \
    --health-check-path /health \
    --health-check-port 5001 \
    --min-instances 1 \
    --max-instances 10 \
    --scale-target-cpu 70 \
    --scale-target-memory 80 || \
koyeb service update ai-search-engine/service \
    --docker-command "python index.py" \
    --port 5001:5001 \
    --env PORT=5001 \
    --env FLASK_ENV=production \
    --env PYTHONUNBUFFERED=1 \
    --env KOYEB_DEPLOYMENT=true

echo "✅ Deployment initiated!"
echo "🌐 Your app will be available at: https://ai-search-engine-your-username.koyeb.app"
echo "📊 Monitor deployment: https://app.koyeb.com/apps/ai-search-engine"
echo ""
echo "🔧 API Endpoints:"
echo "   GET  /search?q=<query> - Search DuckDuckGo"
echo "   GET  /classify?text=<text> - Emotion classification"
echo "   POST /execute - Execute Python code"
echo "   GET  /status - System status"
echo "   GET  /health - Health check"
echo "   GET  /test - Web UI"