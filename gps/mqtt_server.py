import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store the latest location
latest_location = {"latitude": 0, "longitude": 0}

# MQTT Broker details
BROKER_ADDRESS = "localhost"  # Jetson MQTT broker
TOPIC = "location/live"

# Callback when message is received
def on_message(client, userdata, message):
    global latest_location
    payload = message.payload.decode('utf-8')
    print(f"MQTT Message Received: {payload}")

    # Parse latitude and longitude from the message
    try:
        lat, lon = payload.split(",")
        latest_location['latitude'] = float(lat)
        latest_location['longitude'] = float(lon)
        
        # Broadcast location update via WebSocket
        socketio.emit('location_update', latest_location)
    except Exception as e:
        print(f"Error parsing message: {e}")

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER_ADDRESS, 1883)
mqtt_client.subscribe(TOPIC)
mqtt_client.loop_start()

# Serve HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
