#!/bin/bash
echo "🚀 Setting up URL Shortener Application..."

# Create project structure
mkdir -p templates data ssl logs

# Create environment file
if [ ! -f .env ]; then
    cat > .env << 'EOL'
FLASK_ENV=production
PORT=5000
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///data/urls.db
EOL
    echo "✅ Created .env file"
fi

# Copy the frontend template
if [ -f index.html ] && [ ! -f templates/index.html ]; then
    cp index.html templates/index.html
    echo "✅ Copied frontend template"
fi

echo "✅ Project structure created"
echo "📁 Project ready for Docker deployment!"

# Make sure script itself is executable
chmod +x scripts/setup.sh
