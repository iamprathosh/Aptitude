"""
WSGI entry point for Gunicorn to serve the application with Socket.IO support.
This module is specially configured to work with Gunicorn in Replit.
"""

# Import the application and socketio instance
from app import app, socketio

# For Gunicorn, we need to provide the application
# SocketIO does not have a wsgi_app attribute, so let's create the correct wrapper
application = socketio.middleware(app)

# Make app directly accessible for simple WSGI containers
wsgi_app = application

if __name__ == "__main__":
    # Use Flask development server if run directly
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)