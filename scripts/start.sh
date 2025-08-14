#!/bin/bash
echo "🌟 Starting URL Shortener in Development Mode..."
cd ..

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create templates directory if it doesn't exist
mkdir -p templates

# Copy frontend if needed
if [ -f index.html ] && [ ! -f templates/index.html ]; then
    cp index.html templates/index.html
    echo "✅ Copied frontend template"
fi

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=app.py
export PORT=5000

# Start the application
echo "🚀 Starting Flask development server..."
python app.py
EOF

chmod +x start.sh