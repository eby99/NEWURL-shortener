#!/bin/bash
echo "🚄 Deploying to Railway..."

if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "Please login to Railway..."
railway login

railway init
railway variables set FLASK_ENV=production
railway variables set PORT=5000

echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployed to Railway!"
EOF

chmod +x deploy-railway.sh