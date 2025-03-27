#!/bin/bash
# Script to run the application with Gunicorn and Socket.IO support
gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:5000 --reuse-port --reload wsgi:application