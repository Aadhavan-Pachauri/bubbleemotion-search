# 🚀 Koyeb Deployment Guide

## Quick Deploy (2 minutes)

1. **Push to GitHub**
```bash
git add .
git commit -m "Add AI Search Engine with Python Execution API"
git push origin main
```

2. **One-Click Deploy**
```bash
./deploy_koyeb.sh
```

3. **Get Your URL**
Your app will be available at: `https://ai-search-engine-[your-username].koyeb.app`

## Manual Deploy (5 minutes)

### Step 1: Install Koyeb CLI
```bash
# macOS/Linux
curl https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_$(uname -s)_$(uname -m).tar.gz | tar -xz
sudo mv koyeb /usr/local/bin/

# Windows (PowerShell)
# Download from: https://github.com/koyeb/koyeb-cli/releases
```

### Step 2: Login to Koyeb
```bash
koyeb login
```

### Step 3: Create App
```bash
koyeb app create ai-search-engine
```

### Step 4: Deploy Service
```bash
koyeb service create ai-search-engine/service \
  --app ai-search-engine \
  --git github.com/YOUR_USERNAME/YOUR_REPO \
  --git-branch main \
  --port 5001:5001 \
  --env PORT=5001 \
  --env FLASK_ENV=production \
  --env PYTHONUNBUFFERED=1 \
  --env KOYEB_DEPLOYMENT=true \
  --env WORKERS=2 \
  --instance-type free \
  --health-check-path /health \
  --regions was,fra,sin,par,lon,oregon,nyc,tokyo,sydney,saopaulo,mumbai,sweden
```

## 🧪 Test Your Deployment

Replace `ai-search-engine-[your-username].koyeb.app` with your actual URL:

### Test Search
```bash
curl "https://ai-search-engine-[your-username].koyeb.app/search?q=python tutorials"
```

### Test Classification
```bash
curl "https://ai-search-engine-[your-username].koyeb.app/classify?text=I love this amazing product!"
```

### Test Python Execution
```bash
curl -X POST https://ai-search-engine-[your-username].koyeb.app/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello from Koyeb!\")\nprint(\"2 + 2 =\", 2 + 2)"}'
```

### Test Web UI
Open in browser: `https://ai-search-engine-[your-username].koyeb.app/test`

## 📊 Monitoring

- **Dashboard**: https://app.koyeb.com/apps/ai-search-engine
- **Logs**: Available in Koyeb console
- **Metrics**: CPU, memory, request tracking

## 🔧 Configuration Options

### Instance Types
```bash
--instance-type free      # Free tier (1 vCPU, 512MB RAM)
--instance-type nano      # $0.0005/hour (1 vCPU, 512MB RAM)
--instance-type micro     # $0.001/hour (1 vCPU, 1GB RAM)
--instance-type small     # $0.002/hour (1 vCPU, 2GB RAM)
```

### Scaling Options
```bash
--min-instances 1         # Minimum instances
--max-instances 10        # Maximum instances
--scale-target-cpu 70     # Scale at 70% CPU
--scale-target-memory 80  # Scale at 80% memory
```

### Regions
Available regions for deployment:
- **Americas**: `oregon`, `nyc`, `saopaulo`
- **Europe**: `was`, `fra`, `par`, `lon`, `sweden`
- **Asia**: `sin`, `tokyo`, `mumbai`, `sydney`

## 🚨 Troubleshooting

### Build Failures
```bash
# Check logs in Koyeb dashboard
# Test locally first:
docker build -t test .
docker run -p 5001:5001 test
```

### Deployment Issues
```bash
# Verify GitHub connection
koyeb git list

# Check service status
koyeb service get ai-search-engine/service
```

### Runtime Issues
```bash
# Check logs
koyeb service logs ai-search-engine/service

# Test locally
python wsgi.py
```

## 🔄 Updates

To update your deployment:
```bash
# Push new code to GitHub
git add . && git commit -m "Update features" && git push origin main

# Koyeb will automatically redeploy
```

## 🗑️ Cleanup

To remove deployment:
```bash
koyeb service delete ai-search-engine/service
koyeb app delete ai-search-engine
```

## 📞 Support

- **Koyeb Docs**: https://koyeb.com/docs
- **Koyeb Discord**: https://discord.gg/koyeb
- **GitHub Issues**: Report bugs in your repository