from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
import sqlite3
import string
import random
import os
import threading
from datetime import datetime, date
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'urls.db'
lock = threading.Lock()

def init_db():
    """Initialize the database with required tables"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    urls_created INTEGER DEFAULT 0,
                    total_clicks INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

def generate_short_code(length=6):
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DATABASE):
        print("Database not found, initializing...")
        init_db()
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def update_daily_stats(urls_created=0, clicks=0):
    """Update daily statistics"""
    today = date.today().isoformat()
    with lock:
        conn = get_db_connection()
        try:
            existing = conn.execute(
                'SELECT * FROM daily_stats WHERE date = ?', (today,)
            ).fetchone()
            
            if existing:
                conn.execute('''
                    UPDATE daily_stats 
                    SET urls_created = urls_created + ?, total_clicks = total_clicks + ?
                    WHERE date = ?
                ''', (urls_created, clicks, today))
            else:
                conn.execute('''
                    INSERT INTO daily_stats (date, urls_created, total_clicks)
                    VALUES (?, ?, ?)
                ''', (today, urls_created, clicks))
            
            conn.commit()
        finally:
            conn.close()

@app.route('/')
def index():
    """Serve the main application"""
    try:
        # Read the HTML file from the artifact we created
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """
        <h1>URL Shortener</h1>
        <p>Please make sure the templates/index.html file exists.</p>
        <p>You can copy the fixed HTML content from the artifact above.</p>
        """, 500

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Create a shortened URL"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        original_url = (data.get('url') or '').strip()
        custom_code = (data.get('custom_code') or '').strip()
        
        if not original_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not is_valid_url(original_url):
            return jsonify({'error': 'Invalid URL format. Must start with http:// or https://'}), 400
        
        with lock:
            conn = get_db_connection()
            try:
                # Handle custom code
                if custom_code:
                    # Validate custom code
                    if not re.match(r'^[a-zA-Z0-9_-]+$', custom_code):
                        return jsonify({'error': 'Custom code can only contain letters, numbers, hyphens, and underscores'}), 400
                    
                    if len(custom_code) > 20:
                        return jsonify({'error': 'Custom code must be 20 characters or less'}), 400
                    
                    # Check if custom code already exists
                    existing = conn.execute(
                        'SELECT short_code FROM urls WHERE short_code = ?', (custom_code,)
                    ).fetchone()
                    
                    if existing:
                        return jsonify({'error': 'Custom code already exists. Please choose a different one.'}), 400
                    
                    short_code = custom_code
                else:
                    # Generate random short code
                    attempts = 0
                    while attempts < 10:
                        short_code = generate_short_code()
                        existing = conn.execute(
                            'SELECT short_code FROM urls WHERE short_code = ?', (short_code,)
                        ).fetchone()
                        if not existing:
                            break
                        attempts += 1
                    
                    if attempts >= 10:
                        return jsonify({'error': 'Unable to generate unique short code. Please try again.'}), 500
                
                # Insert new URL
                conn.execute('''
                    INSERT INTO urls (short_code, original_url)
                    VALUES (?, ?)
                ''', (short_code, original_url))
                
                conn.commit()
                
                # Update daily stats
                update_daily_stats(urls_created=1)
                
                # Get base URL
                base_url = request.url_root.rstrip('/')
                short_url = f"{base_url}/{short_code}"
                
                return jsonify({
                    'short_url': short_url,
                    'short_code': short_code,
                    'original_url': original_url,
                    'success': True
                })
                
            finally:
                conn.close()
                
    except Exception as e:
        print(f"Error in shorten_url: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    try:
        conn = get_db_connection()
        try:
            # Get total URLs and clicks
            total_stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_urls,
                    COALESCE(SUM(clicks), 0) as total_clicks
                FROM urls
            ''').fetchone()
            
            # Get today's stats
            today = date.today().isoformat()
            today_stats = conn.execute(
                'SELECT urls_created, total_clicks FROM daily_stats WHERE date = ?', (today,)
            ).fetchone()
            
            return jsonify({
                'total_urls': total_stats['total_urls'] or 0,
                'total_clicks': total_stats['total_clicks'] or 0,
                'today_urls': today_stats['urls_created'] if today_stats else 0,
                'today_clicks': today_stats['total_clicks'] if today_stats else 0
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/recent')
def get_recent_urls():
    """Get recent URLs"""
    try:
        conn = get_db_connection()
        try:
            urls = conn.execute('''
                SELECT short_code, original_url, clicks, created_at
                FROM urls
                ORDER BY created_at DESC
                LIMIT 10
            ''').fetchall()
            
            base_url = request.url_root.rstrip('/')
            
            result = []
            for url in urls:
                result.append({
                    'short_code': url['short_code'],
                    'short_url': f"{base_url}/{url['short_code']}",
                    'original_url': url['original_url'],
                    'clicks': url['clicks'] or 0,
                    'created_at': url['created_at']
                })
            
            return jsonify(result)
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in get_recent_urls: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/clear', methods=['DELETE'])
def clear_all_data():
    """Clear all data (for development/testing)"""
    try:
        with lock:
            conn = get_db_connection()
            try:
                conn.execute('DELETE FROM urls')
                conn.execute('DELETE FROM daily_stats')
                conn.commit()
                return jsonify({'message': 'All data cleared successfully'})
            finally:
                conn.close()
                
    except Exception as e:
        print(f"Error in clear_all_data: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to original URL"""
    try:
        # Validate short_code format to prevent injection
        if not re.match(r'^[a-zA-Z0-9_-]+$', short_code):
            return "Invalid short code format", 400
        
        with lock:
            conn = get_db_connection()
            try:
                # Get the original URL
                url_record = conn.execute(
                    'SELECT original_url, clicks FROM urls WHERE short_code = ?', (short_code,)
                ).fetchone()
                
                if not url_record:
                    return """
                    <html>
                    <head><title>URL Not Found</title></head>
                    <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                        <h1>🔍 Short URL Not Found</h1>
                        <p>The requested short URL does not exist or has been removed.</p>
                        <a href="/" style="color: #667eea; text-decoration: none;">← Go back to homepage</a>
                    </body>
                    </html>
                    """, 404
                
                # Increment click count
                conn.execute(
                    'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,)
                )
                conn.commit()
                
                # Update daily click stats
                update_daily_stats(clicks=1)
                
                return redirect(url_record['original_url'])
                
            finally:
                conn.close()
                
    except Exception as e:
        print(f"Error in redirect_to_url: {e}")
        return f"Server error: {str(e)}", 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    print(f"🚀 Starting URL Shortener on port {port}")
    print(f"📍 Access the application at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')