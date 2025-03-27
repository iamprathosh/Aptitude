import requests
import socketio
import time

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server!')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.event
def question_update(data):
    print(f'Received question update: {data}')

# Test HTTP connection first
try:
    print("Testing HTTP connection...")
    response = requests.get('http://localhost:5000/')
    print(f"HTTP Status: {response.status_code}")
    print(f"Content length: {len(response.text)} characters")
    print("HTTP connection successful!\n")
except Exception as e:
    print(f"HTTP connection failed: {e}\n")

# Test Socket.IO connection
try:
    print("Testing Socket.IO connection...")
    sio.connect('http://localhost:5000')
    print("Socket.IO connection established!")
    
    # Wait a bit to receive any initial events
    print("Waiting for events...")
    time.sleep(5)
    
    # Disconnect
    sio.disconnect()
    print("Socket.IO test complete!\n")
except Exception as e:
    print(f"Socket.IO connection failed: {e}\n")

print("All tests completed!")