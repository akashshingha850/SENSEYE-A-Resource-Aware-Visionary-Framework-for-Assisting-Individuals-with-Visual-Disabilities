import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from gtts import gTTS
import datetime
import subprocess
import os
import Jetson.GPIO as GPIO  # Use RPi.GPIO for Jetson devices

# Flask and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
PIN_BUTTON = 40
GPIO.setup(PIN_BUTTON, GPIO.IN)  # Remove pull_up_down

# Latest location data
latest_location = {
    "latitude": 0,
    "longitude": 0,
    "method": "Unknown",
    "location": "Unknown Location",
    "last_update": datetime.datetime.now(),
}

# MQTT Broker details
BROKER_ADDRESS = "localhost"
TOPIC = "location/live"

def set_default_sink_if_available(desired_sink_name):
    """Set the default audio output device to the desired sink if available."""
    try:
        result = subprocess.run(["pactl", "get-default-sink"], stdout=subprocess.PIPE, text=True, check=True)
        current_sink = result.stdout.strip()
        if current_sink == desired_sink_name:
            return
        result = subprocess.run(["pactl", "list", "short", "sinks"], stdout=subprocess.PIPE, text=True, check=True)
        available_sinks = [line.split("\t")[1] for line in result.stdout.splitlines()]
        if desired_sink_name in available_sinks:
            subprocess.run(["pactl", "set-default-sink", desired_sink_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error managing default sink: {e}")

def time_ago(last_update):
    """Calculate how much time has passed since the last update."""
    now = datetime.datetime.now()
    diff = now - last_update
    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    else:
        return f"{int(seconds // 3600)} hours ago"

def on_message(client, userdata, message):
    """Handle incoming MQTT messages."""
    global latest_location
    payload = message.payload.decode("utf-8")
    try:
        parts = payload.split(",", maxsplit=3)
        if len(parts) < 3:
            raise ValueError("Payload does not contain enough values")
        lat, lon, method, location_name = parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else "Unknown Location"
        latest_location.update({
            "latitude": float(lat),
            "longitude": float(lon),
            "method": method,
            "location": location_name,
            "last_update": datetime.datetime.now(),
        })
        socketio.emit("location_update", {
            "latitude": latest_location["latitude"],
            "longitude": latest_location["longitude"],
            "method": latest_location["method"],
            "location": latest_location["location"],
            "last_update": time_ago(latest_location["last_update"]),
        })
    except ValueError as ve:
        print(f"Parsing error: {ve}")
    except Exception as e:
        print(f"Unexpected error parsing MQTT message: {e}")

def speak_location():
    """Use gTTS to speak the current method and location."""
    try:
        text = f"The method is {latest_location['method']}. The location is {latest_location['location']}."
        tts = gTTS(text=text, lang='en')
        tts.save("location.mp3")
        subprocess.run(["mpg123", "location.mp3"], check=True)
        print("Spoken: ", text)
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {e}")
    except Exception as e:
        print(f"Error generating speech: {e}")
    finally:
        if os.path.exists("location.mp3"):
            os.remove("location.mp3")  # Clean up audio file

def button_callback(channel):
    """Handle button press."""
    print("Button pressed! Speaking location...")
    speak_location()

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(BROKER_ADDRESS, 1883)
    mqtt_client.subscribe(TOPIC)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")

# Attach button callback
GPIO.add_event_detect(PIN_BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=300)

@app.route("/")
def index():
    return render_template("index_live.html")

if __name__ == "__main__":
    sink_name = "alsa_output.usb-GN_Netcom_A_S_Jabra_EVOLVE_20_MS_A009E07823660A-00.analog-stereo"
    set_default_sink_if_available(sink_name)
    try:
        print("Starting server...")
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()
