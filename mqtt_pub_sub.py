"""
A complete MQTT pub-sub client using paho-mqtt for the Water ATM system.
This script simulates reading an NFC card UID and handles server authentication
through MQTT messages.

Author: Ruman Ahmed
"""

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import uuid
import json
import logging
import ssl

# -------------------------------------------------------------------
# Setup logger
# -------------------------------------------------------------------
logger = logging.getLogger("atm.mqtt")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# -------------------------------------------------------------------
# MQTT Settings
# -------------------------------------------------------------------
# Put this information in a config file
BROKER = "broker.emqx.io"  # Public broker (use your own for production)
# Default Port
# PORT = 1883
PORT = 8883

# Example topics (should be customized per device or environment)
DEVICE_ID = uuid.getnode()
DEVICE_ID_STR = f"atm-{DEVICE_ID:012x}"
TOPIC_PUB = f"water_atm/{DEVICE_ID_STR}/uid"
TOPIC_SUB = f"water_atm/{DEVICE_ID_STR}/auth"

# -------------------------------------------------------------------
# Callback: When client connects to broker
# -------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info("Connected to MQTT Broker")
        try:
            client.subscribe(TOPIC_SUB)
            logger.info(f"Subscribed to topic: {TOPIC_SUB}")
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
    else:
        logger.error(f"Failed to connect, reason code {reason_code}")

# -------------------------------------------------------------------
# Callback: When message is received
# -------------------------------------------------------------------
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        logger.info(f"Received message on {msg.topic}: {payload}")

        # Process the response
        data = json.loads(payload)
        user_exists = data.get("exists", False)
        balance = data.get("balance", 0)

        if user_exists:
            logger.info(f"User authenticated. Balance: {balance} L")
            # Proceed to enable water dispensing (not implemented here)
        else:
            logger.warning("Authentication failed. User does not exist.")
    except Exception as e:
        logger.error(f"Error while processing incoming message: {e}")

# -------------------------------------------------------------------
# Simulate NFC UID read and publish it
# -------------------------------------------------------------------
def simulate_nfc_uid():
    # In real-world scenario, this will come from your NFC reader hardware
    fake_uid = uuid.uuid4().hex[:8]  # Simulate a UID like "9f8d7a5c"
    return fake_uid

# -------------------------------------------------------------------
# Main Function
# -------------------------------------------------------------------
def main():
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    # Enable TLS using system CA certificates
    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Could not connect to broker: {e}")
        return

    client.loop_start()

    try:
        while True:
            uid = simulate_nfc_uid()
            message = json.dumps({"uid": uid})
            logger.info(f"Publishing UID: {uid} to topic: {TOPIC_PUB}")

            try:
                result = client.publish(TOPIC_PUB, message)
                status = result.rc
                if status == mqtt.MQTT_ERR_SUCCESS:
                    logger.info("UID published successfully")
                else:
                    logger.warning(f"Failed to publish UID. Status: {status}")
            except Exception as e:
                logger.error(f"Error during publish: {e}")

            time.sleep(1)  # Simulate waiting for the next card

    except KeyboardInterrupt:
        logger.info("Disconnecting...")
    finally:
        client.loop_stop()
        client.disconnect()

# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()