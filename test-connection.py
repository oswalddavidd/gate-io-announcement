import time
import json

# pip install websocket_client
from websocket import create_connection

ws = create_connection("wss://api.gateio.ws/ws/v4/ann")
ws.send(json.dumps({
    "time": int(time.time()),
    "channel": "announcement.summary_delisting",
    "event": "subscribe",
    "payload": ["en"]
}))
print(ws.recv())