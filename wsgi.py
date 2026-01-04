#!/usr/bin/env python3
"""
Production WSGI server entry point for Koyeb deployment
Uses Gunicorn for production-ready serving
"""

import os
import sys
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from index import app

if __name__ == "__main__":
    # Production mode - get configuration from environment
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0'
    workers = int(os.environ.get('WORKERS', 2))
    
    # Only use Gunicorn if available, otherwise fallback to Flask
    try:
        import gunicorn
        
        # Create Gunicorn configuration
        gunicorn_config = {
            'bind': f'{host}:{port}',
            'workers': workers,
            'worker_class': 'sync',
            'timeout': 120,
            'keepalive': 5,
            'max_requests': 1000,
            'max_requests_jitter': 50,
            'preload_app': True,
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'info'
        }
        
        # Run with Gunicorn
        from gunicorn.app.base import BaseApplication
        
        class FlaskApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        logging.info(f"🚀 Starting production server with {workers} workers on {host}:{port}")
        FlaskApplication(app, gunicorn_config).run()
        
    except ImportError:
        # Fallback to Flask development server
        logging.warning("⚠️  Gunicorn not available, using Flask development server")
        logging.info(f"🚀 Starting development server on {host}:{port}")
        
        app.run(
            host=host,
            port=port,
            debug=False,  # Never debug in production
            threaded=True,
            use_reloader=False
        )