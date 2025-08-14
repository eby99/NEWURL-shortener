from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
import sqlite3
import string
import random
import os
import threading
from datetime import datetime, date
import json

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'urls.db'
lock = threading.Lock()

def init_db():
    """Initialize the database with required tables"""
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

def generate_short_code(length=6):
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def update_daily_stats(urls_created=0, clicks=0):
    """Update daily statistics"""
    today = date.today().isoformat()
    with lock:
        conn = get_db_connection()
        try:
            # Check if record exists for today
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
    with open('templates/index.html', 'r') as f:
        return render_template_string(f.read())

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Create a shortened URL"""
    try:
        data = request.get_json()
        original_url = data.get('url', '').strip()
        custom_code = data.get('custom_code', '').strip()
        
        if not original_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not (original_url.startswith('http://') or original_url.startswith('https://')):
            return jsonify({'error': 'URL must start with http:// or https://'}), 400
        
        with lock:
            conn = get_db_connection()
            try:
                # Handle custom code
                if custom_code:
                    # Validate custom code
                    if not all(c.isalnum() or c in '-_' for c in custom_code):
                        return jsonify({'error': 'Custom code can only contain letters, numbers, hyphens, and underscores'}), 400
                    
                    # Check if custom code already exists
                    existing = conn.execute(
                        'SELECT short_code FROM urls WHERE short_code = ?', (custom_code,)
                    ).fetchone()
                    
                    if existing:
                        return jsonify({'error': 'Custom code already exists'}), 400
                    
                    short_code = custom_code
                else:
                    # Generate random short code
                    while True:
                        short_code = generate_short_code()
                        existing = conn.execute(
                            'SELECT short_code FROM urls WHERE short_code = ?', (short_code,)
                        ).fetchone()
                        if not existing:
                            break
                
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
                    'original_url': original_url
                })
                
            finally:
                conn.close()
                
    except Exception as e:
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
                'total_urls': total_stats['total_urls'],
                'total_clicks': total_stats['total_clicks'],
                'today_urls': today_stats['urls_created'] if today_stats else 0,
                'today_clicks': today_stats['total_clicks'] if today_stats else 0
            })
            
        finally:
            conn.close()
            
    except Exception as e:
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
                    'clicks': url['clicks'],
                    'created_at': url['created_at']
                })
            
            return jsonify(result)
            
        finally:
            conn.close()
            
    except Exception as e:
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
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to original URL"""
    try:
        with lock:
            conn = get_db_connection()
            try:
                # Get the original URL
                url_record = conn.execute(
                    'SELECT original_url, clicks FROM urls WHERE short_code = ?', (short_code,)
                ).fetchone()
                
                if not url_record:
                    return "Short URL not found", 404
                
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
        return f"Server error: {str(e)}", 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')