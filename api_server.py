#!/usr/bin/env python3
"""Flask API with working DuckDuckGo scraper."""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from simple_ddg_scraper import scrape_ddg_html

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Search endpoint using DuckDuckGo scraper."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    try:
        print(f"[API] Searching for: {query}")
        results = scrape_ddg_html(query, max_results=10)
        print(f"[API] Found {len(results)} results")
        return jsonify(results)
    
    except Exception as e:
        print(f"[API] Error searching: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[API] Starting Flask API with DuckDuckGo scraper...")
    print("[API] Available endpoints:")
    print("[API]   GET / - Main page")
    print("[API]   GET /search?q=<query> - Search endpoint")
    
    app.run(host='127.0.0.1', port=5001, debug=True)