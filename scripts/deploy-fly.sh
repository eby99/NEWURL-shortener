#!/bin/bash
echo "🪰 Deploying to Fly.io..."

if ! command -v flyctl &> /dev/null; then
    echo "Installing Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

echo "Please login to Fly.io..."
flyctl auth login

cd ..
if [ ! -f "fly.toml" ]; then
    echo "🚀 Launching new Fly.io app..."
    flyctl launch --no-deploy
fi

echo "💾 Creating persistent volume..."
flyctl volumes create url_shortener_data --size 1

echo "🔐 Setting environment variables..."
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)

echo "🚀 Deploying to Fly.io..."
flyctl deploy

echo "✅ Deployed to Fly.io!"
EOF

chmod +x deploy-fly.sh