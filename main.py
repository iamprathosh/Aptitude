import eventlet
eventlet.monkey_patch()

from app import app, socketio

# Make app importable by gunicorn
application = app

# This is for Gunicorn to import and use with the eventlet worker
# The workflow config uses: gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
# But Gunicorn with Socket.IO needs to use the Socket.IO instance
from eventlet import wsgi
import eventlet

def serve_eventlet():
    """Function to serve with eventlet directly"""
    wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)

if __name__ == "__main__":
    # Use Flask development server with eventlet worker
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
