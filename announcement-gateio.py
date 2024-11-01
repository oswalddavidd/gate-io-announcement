import time
import json
import requests
from datetime import datetime
from websocket import create_connection

# Set your bot token and chat ID
TELEGRAM_TOKEN = "7927662834:AAFcBeR28-67zAGE0ksSs7EwlIjGWq6GPbg"
CHAT_ID = "-4570309964"

# Define a function to convert Unix timestamp to human-readable format
def format_timestamp(unix_time, unix_time_ms):
    # Convert seconds and milliseconds to a single datetime object
    timestamp = datetime.fromtimestamp(unix_time)
    # Format the datetime object as a string
    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    # Add milliseconds if necessary
    if unix_time_ms:
        milliseconds = unix_time_ms % 1000  # Get milliseconds
        formatted_time += f".{milliseconds:03d}"
    return formatted_time

# Define a function to send messages to Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Parse the incoming message
    message_data = json.loads(message)

    # Extract the relevant fields
    time_received = message_data.get("time")
    time_ms = message_data.get("time_ms")
    origin_url = message_data.get("result", {}).get("origin_url")
    title = message_data.get("result", {}).get("title")

    # Only send the message if it has the relevant fields
    if origin_url and title:
        # Format the time for Telegram
        formatted_time = format_timestamp(time_received, time_ms)
        
        # Format the message for Telegram
        telegram_message = (
            f"Time: {formatted_time}\n"
            f"Origin URL: {origin_url}\n"
            f"Title: {title}"
        )
        
        payload = {
            "chat_id": CHAT_ID,
            "text": telegram_message
        }
        headers = {
            "Content-Type": "application/json"
        }
        # Send message to Telegram
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Failed to send message to Telegram:", response.text)
        else:
            print("Message sent to Telegram successfully")

# Define the function to connect to the WebSocket and handle messages
def run_websocket():
    try:
        ws = create_connection("wss://api.gateio.ws/ws/v4/ann")
        
        # Subscribe to the channel
        ws.send(json.dumps({
            "time": int(time.time()),
            "channel": "announcement.summary_delisting",
            "event": "subscribe",
            "payload": ["en"]
        }))
        
        print("Connected and subscribed to channel.")
        
        # Continuous loop to keep receiving messages
        while True:
            try:
                # Receive message
                message = ws.recv()
                
                # Process or print the message
                print("Received message:", message)
                
                # Check if the message is an update before sending
                message_data = json.loads(message)
                if message_data.get("event") == "update":
                    # Send message to Telegram
                    send_to_telegram(message)
            
            except Exception as e:
                print("Error while receiving message:", e)
                break
    
    except Exception as e:
        print("Connection error:", e)
    finally:
        ws.close()
        print("WebSocket connection closed.")

# Run the WebSocket
run_websocket()
