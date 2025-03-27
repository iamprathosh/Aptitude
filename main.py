import eventlet
eventlet.monkey_patch()

from app import app, socketio

if __name__ == "__main__":
    # Use Flask development server for direct running
    # but gunicorn will be used in the workflow
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
