
#!/bin/bash
echo "🧹 Cleaning up URL Shortener..."

cd ..
docker-compose down
docker rmi url-shortener_url-shortener 2>/dev/null || true
docker system prune -f

if [ -d "venv" ]; then
    rm -rf venv
fi

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Cleanup completed!"
EOF

cat > logs.sh << 'EOF'
#!/bin/bash
echo "📝 Showing URL Shortener logs..."

cd ..