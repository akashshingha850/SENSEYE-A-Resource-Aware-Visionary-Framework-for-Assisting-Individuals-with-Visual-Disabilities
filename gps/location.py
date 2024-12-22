import Jetson.GPIO as GPIO
import serial
import time
import paho.mqtt.client as mqtt
import requests

# MQTT Broker Configuration
BROKER_ADDRESS = "localhost"  # Replace with the actual broker address
TOPIC = "location/live"

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER_ADDRESS, 1883)

# Serial Port Configuration
ser = serial.Serial('/dev/ttyTHS1', 115200)
ser.flushInput()

# GPIO Configuration
powerKey = 6

# Function to send AT commands
def sendAt(command, back, timeout):
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        rec_buff = ser.read(ser.inWaiting())
        if rec_buff.decode().find(back) != -1:
            return rec_buff.decode()
    return None

# Function to get GPS location
def getGpsPosition():
    print("Attempting to get GPS location...")
    sendAt("AT+CGPS=1,2", "OK", 1)
    time.sleep(2)
    gps_info = sendAt("AT+CGPSINFO", "+CGPSINFO: ", 1)
    if gps_info:
        data = gps_info.split(":")[1].strip()
        if data and data != ",,,,,,,,":
            lat, lon = data.split(",")[:2]
            if lat and lon:
                print(f"GPS Location: {lat}, {lon}")
                return float(lat), float(lon)
    print("No valid GPS data available.")
    return None

# Function to get location from IP
def getIpLocation():
    print("Falling back to IP-based location...")
    try:
        ip_response = requests.get("https://api.ipify.org?format=json")
        ip = ip_response.json().get("ip")
        loc_response = requests.get(f"http://ip-api.com/json/{ip}")
        if loc_response.status_code == 200:
            loc_data = loc_response.json()
            lat, lon = loc_data.get("lat"), loc_data.get("lon")
            print(f"IP Location: {lat}, {lon}")
            return lat, lon
    except Exception as e:
        print(f"Error getting IP location: {e}")
    return None

# Power on the SIM7600X module
def powerOn():
    print("Powering on SIM7600X...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(powerKey, GPIO.OUT)
    GPIO.output(powerKey, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(powerKey, GPIO.LOW)
    time.sleep(20)
    print("SIM7600X is ready.")

# Power off the SIM7600X module
def powerDown():
    print("Powering off SIM7600X...")
    GPIO.output(powerKey, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(powerKey, GPIO.LOW)
    time.sleep(18)
    print("SIM7600X is off.")

# Main publishing loop
def publish_location():
    try:
        powerOn()
        while True:
            location = getGpsPosition()
            if not location:
                location = getIpLocation()
            
            if location:
                lat, lon = location
                payload = f"{lat},{lon}"
                mqtt_client.publish(TOPIC, payload)
                print(f"Published: {payload}")
            else:
                print("Failed to obtain location.")

            # Retry GPS after a delay
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping location publishing.")
    finally:
        powerDown()
        mqtt_client.disconnect()
        GPIO.cleanup()

# Start publishing
if __name__ == "__main__":
    publish_location()
