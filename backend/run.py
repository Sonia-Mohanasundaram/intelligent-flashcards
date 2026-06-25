#!/usr/bin/env python
"""Entry point for the Flask application"""

import os
import sys
from app import create_app
from config import Config

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from config
    host = Config.SERVER_HOST
    port = Config.SERVER_PORT
    debug = Config.DEBUG
    
    print(f"\n{'='*60}")
    print(f"Smart Flashcard AI Backend")
    print(f"{'='*60}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"{'='*60}\n")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)
