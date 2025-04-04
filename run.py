import os
from app import app, socketio

if __name__ == "__main__":
    # Use Socket.IO with the Flask development server
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)