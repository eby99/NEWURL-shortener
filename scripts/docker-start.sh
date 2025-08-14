#!/bin/bash
echo "🐳 Starting URL Shortener with Docker..."

# Create necessary directories
mkdir -p data templates ssl

# Copy frontend template if exists
if [ -f ../index.html ] && [ ! -f ../templates/index.html ]; then
    cp ../index.html ../templates/index.html
    echo "✅ Frontend template ready"
fi

# Build and start with Docker Compose
echo "Building and starting containers..."
cd ..
docker-compose up --build -d

echo "✅ Application started successfully!"
echo "🌐 Access your application at: http://localhost:5000"
echo "📊 Health check available at: http://localhost:5000/health"

# Show logs
echo "📝 Showing application logs (Ctrl+C to stop):"
docker-compose logs -f
EOF

chmod +x docker-start.sh