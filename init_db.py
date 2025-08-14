#!/usr/bin/env python3
"""
Database initialization script for URL Shortener
Run this script to create the required database tables
"""

import sqlite3
import os

DATABASE = 'urls.db'

def init_database():
    """Initialize the database with required tables"""
    print(f"Initializing database: {DATABASE}")
    
    # Remove existing database if it exists (optional - uncomment if you want fresh start)
    # if os.path.exists(DATABASE):
    #     os.remove(DATABASE)
    #     print("Removed existing database")
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            # Create urls table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create daily_stats table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    urls_created INTEGER DEFAULT 0,
                    total_clicks INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            print("✅ Database tables created successfully!")
            
            # Verify tables were created
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("\nCreated tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Database initialization completed!")
        print("You can now run your Flask application.")
    else:
        print("\n💥 Database initialization failed!")