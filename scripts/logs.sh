#!/bin/bash
echo "📝 Showing URL Shortener logs..."

cd ..
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
if docker-compose ps | grep -q "Up"; then
   echo "📊 Container Status:"
   docker-compose ps
   echo ""
   echo "📝 Application Logs (Press Ctrl+C to stop):"
   docker-compose logs -f --tail=50
else
   echo "❌ Docker containers are not running"
   echo "Start them with: ./scripts/docker-start.sh"
fi
EOF

chmod +x cleanup.sh logs.sh