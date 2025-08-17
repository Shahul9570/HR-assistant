#!/usr/bin/env python3
"""
HR AI Agent - Main Runner Script
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import os
import sys
from backend.app import app

if __name__ == '__main__':
    # Set environment variables if not already set
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    print("=" * 50)
    print("HR AI Agent - Resume Screening System")
    print("=" * 50)
    print("Starting Flask application...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 50)
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nShutting down HR AI Agent...")
        sys.exit(0)