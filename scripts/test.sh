#!/bin/bash
echo "🧪 Running application tests..."

# Wait for application to be ready
sleep 5

BASE_URL="http://localhost:5000"

# Test health endpoint
echo "Testing health check..."
curl -f $BASE_URL/health || { echo "❌ Health check failed"; exit 1; }

# Test URL shortening
echo "Testing URL shortening..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url/that/needs/shortening"}')

echo "Response: $RESPONSE"

if echo $RESPONSE | grep -q "short_url"; then
    echo "✅ URL shortening successful"
else
    echo "❌ URL shortening failed"
    exit 1
fi

echo "✅ All tests passed!"
EOF

chmod +x test.sh