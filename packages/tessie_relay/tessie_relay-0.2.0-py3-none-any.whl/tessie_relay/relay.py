import os
import paho.mqtt.client as mqtt
from questdb.ingress import Sender, TimestampNanos
import time
import threading
from .payload_types import payload_types
from .helpers import convert_payload

# QuestDB configuration
if os.environ.get("QDB_CLIENT_CONF") is None:
    raise ValueError("QDB_CLIENT_CONF environment variable not set")

# Array of MQTT hostnames
mqtt_hosts = ["coldbox01.psi.ch", "coldbox02.psi.ch"]


def write_to_questdb(payload_type, data, source):
    with Sender.from_env() as sender:
        
        if payload_type in ["Env", "VAR"]:
            # Handle 'Env' and 'VAR' payloads as dictionaries
            for key, value in data.items():
                # Skip if value is 'nan' or None
                if value is None or str(value).lower() == "nan":
                    continue
                sender.row(
                    source,  # table name
                    symbols={'type': payload_type},  # tags
                    columns={key: value},  # fields
                    at=TimestampNanos.now()
                )
        elif isinstance(data, list):
            # Handle list-based payloads (e.g., 'Peltier_U', 'Peltier_I')
            for peltier_id, value in enumerate(data, start=1):
                if value is None or str(value).lower() == "nan":
                    continue
                sender.row(
                    source,  # table name
                    symbols={
                        'type': 'tec_value',
                        'tec_id': str(peltier_id)
                    },
                    columns={payload_type: value},
                    at=TimestampNanos.now()
                )
        else:
            print(f"Invalid data format for {payload_type}: {data}")

# Parse incoming MQTT message
def parse_message(msg, source):
    payload = msg.payload.decode()
    # print(f"Received payload: {payload}")
    converted_payload = convert_payload(payload)

    payload_type = list(converted_payload.keys())[0]
    data = converted_payload[payload_type]

    # Check if the data is a list or a dictionary before calling write_to_questdb
    if isinstance(data, dict) or isinstance(data, list):
        write_to_questdb(payload_type, data, source)
    else:
        print(f"Unexpected data type for payload: {type(data)}")

# MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties=None):
    source = userdata["source"]
    if reason_code == 0:
        print(f"Connected to {source} successfully.")
        client.subscribe("monTessie")
    else:
        print(f"Failed to connect to {source}, reason code: {reason_code}. Retrying...")

def reconnect(client, source):
    while True:
        try:
            print(f"Attempting to reconnect to {source}...")
            client.reconnect()
            print(f"Successfully reconnected to {source}.")
            break  # Exit the loop on successful reconnection
        except Exception as e:
            print(f"Reconnection to {source} failed: {e}. Retrying in 60 seconds...")
            time.sleep(60)

def on_disconnect(client, userdata, reason_code, properties=None):
    source = userdata["source"]
    print(f"Disconnected from {source}. Reason code: {reason_code}. Starting reconnection thread...")
    # Start a separate thread for reconnection
    threading.Thread(target=reconnect, args=(client, source), daemon=True).start()

def on_message(client, userdata, msg):
    source = userdata["source"]
    # print(f"Message received from {source}: {msg.payload.decode()}")
    # Your message processing logic
    parse_message(msg, source)

# Main function to initialize MQTT clients for each source
def main():
    print("Starting tessie-relay...")

    clients = []

    for host in mqtt_hosts:
        # Use explicit protocol version 5
        client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.user_data_set({"source": host})
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        try:
            client.connect(host, 1883, 60)
        except Exception as e:
            print(f"Initial connection to {host} failed: {e}. Will attempt reconnection in the background.")
        
        client.reconnect_delay_set(min_delay=5, max_delay=60)
        clients.append(client)

    # Start all clients in separate threads
    for client in clients:
        client.loop_start()

    try:
        while True:
            time.sleep(1)  # Prevent busy-waiting
    except KeyboardInterrupt:
        print("Shutting down...")
        for client in clients:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    main()