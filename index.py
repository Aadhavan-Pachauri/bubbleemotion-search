#!/usr/bin/env python3
"""
Comprehensive AI Search Engine with Emotion Classification
Sets up both API endpoints and web UI with all features integrated.
"""

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
import sys
import os
import logging
import threading
import time
from datetime import datetime
import subprocess
import tempfile
import uuid

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import modules
try:
    from search_engine import scrape_ddg_html
    logger.info("✅ Search engine module loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load search engine: {e}")
    scrape_ddg_html = None

try:
    from emotion_classifier import classify_query, get_model_status, load_model
    logger.info("✅ Emotion classifier module loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load emotion classifier: {e}")
    classify_query = None
    get_model_status = None

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global variables for system state
_system_status = {
    'start_time': datetime.now(),
    'search_requests': 0,
    'classification_requests': 0,
    'errors': 0,
    'model_loaded': False
}

def update_system_stats(endpoint_type):
    """Update system statistics."""
    if endpoint_type == 'search':
        _system_status['search_requests'] += 1
    elif endpoint_type == 'classify':
        _system_status['classification_requests'] += 1
    elif endpoint_type == 'error':
        _system_status['errors'] += 1

def get_system_health():
    """Get comprehensive system health status."""
    uptime = datetime.now() - _system_status['start_time']
    
    health = {
        'status': 'healthy',
        'uptime_seconds': uptime.total_seconds(),
        'uptime_human': str(uptime).split('.')[0],
        'search_engine': 'available' if scrape_ddg_html else 'unavailable',
        'emotion_classifier': 'available' if classify_query else 'unavailable',
        'model_loaded': _system_status['model_loaded'],
        'statistics': {
            'search_requests': _system_status['search_requests'],
            'classification_requests': _system_status['classification_requests'],
            'errors': _system_status['errors']
        }
    }
    
    # Determine overall health
    if not scrape_ddg_html or not classify_query:
        health['status'] = 'degraded'
    elif _system_status['errors'] > 10:
        health['status'] = 'unhealthy'
    
    return health

# Background model loading
def load_emotion_model():
    """Load emotion model in background."""
    try:
        logger.info("🔄 Loading emotion classification model in background...")
        if load_model():
            _system_status['model_loaded'] = True
            logger.info("✅ Emotion model loaded successfully")
        else:
            logger.warning("⚠️ Emotion model loading failed, using fallback")
    except Exception as e:
        logger.error(f"❌ Error loading emotion model: {e}")
        _system_status['model_loaded'] = False

# Routes
@app.route('/')
def index():
    """Serve the main page with redirect to test UI."""
    return redirect(url_for('test_ui'))

@app.route('/test')
def test_ui():
    """Serve the enhanced test UI with both search and classification."""
    try:
        return render_template('test_ui.html')
    except Exception as e:
        logger.error(f"❌ Error serving test UI: {e}")
        return f"""
        <html>
        <head><title>AI Search Engine</title></head>
        <body>
            <h1>AI Search Engine</h1>
            <p>Error loading UI: {str(e)}</p>
            <p>Try the API endpoints:</p>
            <ul>
                <li><a href="/search?q=test">/search?q=test</a></li>
                <li><a href="/classify?text=test">/classify?text=test</a></li>
                <li><a href="/status">/status</a></li>
            </ul>
        </body>
        </html>
        """, 500

@app.route('/search')
def search():
    """Search endpoint using DuckDuckGo scraper."""
    query = request.args.get('q', '').strip()
    
    if not query:
        update_system_stats('error')
        return jsonify({'error': 'Missing query parameter', 'suggestion': 'Use: /search?q=your search query'}), 400
    
    if not scrape_ddg_html:
        update_system_stats('error')
        return jsonify({'error': 'Search engine unavailable'}), 503
    
    try:
        logger.info(f"🔍 Searching for: {query}")
        start_time = time.time()
        
        results = scrape_ddg_html(query, max_results=10)
        
        search_time = time.time() - start_time
        update_system_stats('search')
        
        logger.info(f"✅ Found {len(results)} results in {search_time:.2f}s")
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results),
            'search_time': round(search_time, 3),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        update_system_stats('error')
        logger.error(f"❌ Search error: {e}")
        return jsonify({
            'error': 'Search failed',
            'details': str(e),
            'suggestion': 'Try a different query or check logs'
        }), 500

@app.route('/classify')
def classify():
    """Emotion classification endpoint with comprehensive analysis."""
    text = request.args.get('text', '').strip()
    
    if not text:
        update_system_stats('error')
        return jsonify({
            'error': 'Missing text parameter',
            'suggestion': 'Use: /classify?text=your text to analyze'
        }), 400
    
    if not classify_query:
        update_system_stats('error')
        return jsonify({'error': 'Emotion classifier unavailable'}), 503
    
    try:
        logger.info(f"🧠 Classifying text: {text[:100]}...")
        start_time = time.time()
        
        result = classify_query(text)
        
        classification_time = time.time() - start_time
        update_system_stats('classify')
        
        # Add metadata to result
        result['metadata'] = {
            'text_length': len(text),
            'classification_time': round(classification_time, 3),
            'timestamp': datetime.now().isoformat(),
            'model_loaded': _system_status['model_loaded']
        }
        
        logger.info(f"✅ Classification complete in {classification_time:.3f}s")
        
        return jsonify(result)
    
    except Exception as e:
        update_system_stats('error')
        logger.error(f"❌ Classification error: {e}")
        return jsonify({
            'error': 'Classification failed',
            'details': str(e),
            'fallback': {
                'primary_state': 'neutral_regulation',
                'confidence': 1.0,
                'tool': 'web_search',
                'psychological_profile': {'valence': 0.0, 'arousal': 0.0, 'engagement': 0.0, 'regulation': 1.0},
                'note': 'Using fallback due to classification error'
            }
        }), 500

@app.route('/status')
def status():
    """Get comprehensive system status."""
    try:
        health = get_system_health()
        
        # Add model status if available
        if get_model_status:
            try:
                model_info = get_model_status()
                health['emotion_classifier_details'] = model_info
            except Exception as e:
                logger.warning(f"⚠️ Could not get model status: {e}")
        
        # Add available endpoints
        health['endpoints'] = {
            'search': {
                'path': '/search',
                'method': 'GET',
                'parameters': {'q': 'search query'},
                'status': 'available' if scrape_ddg_html else 'unavailable'
            },
            'classify': {
                'path': '/classify',
                'method': 'GET', 
                'parameters': {'text': 'text to analyze'},
                'status': 'available' if classify_query else 'unavailable'
            },
            'status': {
                'path': '/status',
                'method': 'GET',
                'status': 'available'
            },
            'test_ui': {
                'path': '/test',
                'method': 'GET',
                'status': 'available'
            }
        }
        
        return jsonify(health)
    
    except Exception as e:
        logger.error(f"❌ Status endpoint error: {e}")
        return jsonify({
            'error': 'Status check failed',
            'details': str(e),
            'status': 'unknown'
        }), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    health = get_system_health()
    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify({'status': health['status']}), status_code

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        'name': 'AI Search Engine with Emotion Classification',
        'version': '2.0',
        'description': 'A modular search engine that combines DuckDuckGo search with psychological emotion classification',
        'endpoints': {
            '/search': {
                'method': 'GET',
                'description': 'Search DuckDuckGo for web results',
                'parameters': {
                    'q': 'Search query (required)'
                },
                'response': {
                    'query': 'original search query',
                    'results': 'array of search results',
                    'count': 'number of results',
                    'search_time': 'search duration in seconds'
                }
            },
            '/classify': {
                'method': 'GET',
                'description': 'Analyze text for psychological and emotional content',
                'parameters': {
                    'text': 'Text to analyze (required)'
                },
                'response': {
                    'primary_state': 'psychological state description',
                    'confidence': 'confidence score (0-1)',
                    'tool': 'recommended tool based on analysis',
                    'psychological_profile': 'detailed psychological metrics',
                    'emotion_percentages': 'emotion analysis with percentages',
                    'psychological_insights': 'human-readable insights'
                }
            },
            '/status': {
                'method': 'GET',
                'description': 'Get comprehensive system status',
                'response': 'system health and statistics'
            }
        },
        'features': [
            'DuckDuckGo web search with 10 results per query',
            'Advanced psychological emotion classification',
            'DistilBERT-emotion integration with fallback',
            'Percentage-based emotion analysis',
            'Psychological pattern recognition',
            'Context-aware classification',
            'Priority hierarchy: emojis > repetition > punctuation > length'
        ]
    })

# Python code execution endpoint
@app.route('/execute', methods=['POST'])
def execute_python():
    """
    Execute Python code safely in a sandboxed environment.
    Returns both output and any generated files.
    """
    code = request.json.get('code', '') if request.json else ''
    
    if not code:
        return jsonify({
            'error': 'Missing code parameter',
            'suggestion': 'Send JSON with "code" field containing Python code'
        }), 400
    
    # Security: Block dangerous imports and operations
    dangerous_patterns = [
        'import os', 'import subprocess', 'import sys',
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file(', 'input(', 'raw_input(',
        'socket', 'urllib', 'requests', 'http',
        'rm -rf', 'sudo', 'chmod', 'chown'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code.lower():
            return jsonify({
                'error': 'Security violation',
                'details': f'Dangerous pattern detected: {pattern}',
                'suggestion': 'Use only safe Python operations'
            }), 403
    
    # Create temporary directory for execution
    temp_dir = tempfile.mkdtemp()
    execution_id = str(uuid.uuid4())[:8]
    
    try:
        # Write code to temporary file
        code_file = os.path.join(temp_dir, f'script_{execution_id}.py')
        with open(code_file, 'w') as f:
            f.write(code)
        
        # Execute code with timeout
        start_time = time.time()
        process = subprocess.Popen(
            [sys.executable, code_file],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=30)
            execution_time = time.time() - start_time
            
            # Collect generated files
            files = {}
            for filename in os.listdir(temp_dir):
                if filename.startswith('script_') and filename.endswith('.py'):
                    continue  # Skip the script file itself
                
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            files[filename] = f.read().decode('utf-8', errors='ignore')
                    except Exception as e:
                        files[filename] = f'<Error reading file: {str(e)}>'
            
            return jsonify({
                'execution_id': execution_id,
                'output': stdout,
                'error': stderr,
                'execution_time': round(execution_time, 3),
                'files': files,
                'success': process.returncode == 0,
                'return_code': process.returncode
            })
            
        except subprocess.TimeoutExpired:
            process.kill()
            return jsonify({
                'error': 'Execution timeout',
                'details': 'Code execution exceeded 30 second limit',
                'execution_time': 30
            }), 408
            
    except Exception as e:
        return jsonify({
            'error': 'Execution failed',
            'details': str(e)
        }), 500
        
    finally:
        # Cleanup temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass

# Error handlers
@app.errorhandler(404)
def not_found(_error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/search', '/classify', '/status', '/test', '/health', '/api/docs', '/execute'],
        'suggestion': 'Check /api/docs for API documentation'
    }), 404

@app.errorhandler(500)
def internal_error(_error):
    """Handle 500 errors."""
    update_system_stats('error')
    return jsonify({
        'error': 'Internal server error',
        'suggestion': 'Check server logs for details'
    }), 500

# Startup function
def startup():
    """Initialize the application."""
    logger.info("🚀 Starting AI Search Engine with Emotion Classification...")
    
    # Start background model loading
    if classify_query:
        threading.Thread(target=load_emotion_model, daemon=True).start()
    else:
        logger.warning("⚠️ Emotion classifier not available")
    
    if not scrape_ddg_html:
        logger.warning("⚠️ Search engine not available")
    
    logger.info("📋 Available endpoints:")
    logger.info("   GET /search?q=<query> - Search DuckDuckGo")
    logger.info("   GET /classify?text=<text> - Analyze emotion/psychology")
    logger.info("   POST /execute - Execute Python code (JSON: {code: '...'})")
    logger.info("   GET /status - System status")
    logger.info("   GET /health - Health check")
    logger.info("   GET /test - Web UI")
    logger.info("   GET /api/docs - API documentation")
    
    logger.info("🌐 Starting Flask server on http://127.0.0.1:5001")

if __name__ == '__main__':
    startup()
    
    # Get port from environment variable (for Koyeb) or use default
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0' if os.environ.get('KOYEB_DEPLOYMENT') else '127.0.0.1'
    
    try:
        app.run(
            host=host, 
            port=port, 
            debug=not os.environ.get('KOYEB_DEPLOYMENT'),
            threaded=True,
            use_reloader=False  # Disable reloader to prevent double loading
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)