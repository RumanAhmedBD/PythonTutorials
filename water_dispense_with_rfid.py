'''
A complete MQTT pub-sub client using paho-mqtt for the Water ATM system.
This script simulates reading an NFC card UID, handles server authentication
through MQTT messages, and simulates water dispensing with flow sensor feedback.

Author: Ruman Ahmed
'''

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import uuid
import json
import logging
import ssl
import random
from mfrc522 import SimpleMFRC522

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
BROKER = "broker.emqx.io"
PORT = 8883
DEVICE_ID = uuid.getnode()
DEVICE_ID_STR = f"atm-{DEVICE_ID:012x}"
TOPIC_PUB_UID = f"water_atm/{DEVICE_ID_STR}/uid"
TOPIC_PUB_RESULT = f"water_atm/{DEVICE_ID_STR}/result"
TOPIC_SUB_AUTH = f"water_atm/{DEVICE_ID_STR}/auth"
TOPIC_SUB_CONFIRM = f"water_atm/{DEVICE_ID_STR}/confirm"

authenticated = False
balance = 0
current_card_uid = None
reader = SimpleMFRC522()

# -------------------------------------------------------------------
# Callback: When client connects to broker
# -------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info("Connected to MQTT Broker")
        try:
            client.subscribe(TOPIC_SUB_AUTH, qos=0)
            client.subscribe(TOPIC_SUB_CONFIRM, qos=0)
            logger.info(f"Subscribed to topics: {TOPIC_SUB_AUTH}, {TOPIC_SUB_CONFIRM}")
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
    else:
        logger.error(f"Failed to connect, reason code {reason_code}")

# -------------------------------------------------------------------
# Callback: When message is received
# -------------------------------------------------------------------
def on_message(client, userdata, msg):
    global authenticated, balance
    try:
        if msg.retain:
            logger.warning("Retained message received. Ignoring.")
            return

        payload = msg.payload.decode()
        logger.info(f"Received message on {msg.topic}: {payload}")
        data = json.loads(payload)

        if msg.topic == TOPIC_SUB_AUTH:
            user_exists = data.get("exists", False)
            balance = data.get("balance", 0)

            if user_exists:
                authenticated = True
                logger.info(f"User authenticated. Balance: {balance} L")
                start_dispensing(client)
                authenticated = False
            else:
                logger.warning("Authentication failed. User does not exist.")

        elif msg.topic == TOPIC_SUB_CONFIRM:
            server_confirm = data.get("updated", False)
            if server_confirm:
                logger.info("Server confirmed balance update.")
            else:
                logger.warning("Server failed to confirm balance update.")

    except Exception as e:
        logger.error(f"Error while processing incoming message: {e}")

# -------------------------------------------------------------------
# Callback: When client disconnects from broker
# -------------------------------------------------------------------
def on_disconnect(client, userdata, rc, properties=None):
    logger.warning("Disconnected from MQTT broker")
    while True:
        try:
            logger.info("Attempting to reconnect...")
            client.reconnect()
            logger.info("Reconnected successfully")
            break
        except Exception as e:
            logger.error(f"Reconnect failed: {e}")
            time.sleep(5)

# -------------------------------------------------------------------
# Start dispensing with real-time card validation
# -------------------------------------------------------------------
def start_dispensing(client):
    global balance, current_card_uid
    logger.info("Starting water dispensing...")

    initial_uid = current_card_uid
    total_pulses = 0
    start_time = time.time()
    duration = 5  # seconds

    while time.time() - start_time < duration:
        try:
            uid, _ = reader.read()
            if uid != initial_uid:
                logger.warning("Card changed. Stopping water dispensing.")
                break
        except Exception:
            logger.warning("Card removed. Stopping water dispensing.")
            break

        pulses = random.randint(1, 5)
        total_pulses += pulses
        time.sleep(0.2)

    dispensed_ml = total_pulses * 2
    dispensed_liters = round(dispensed_ml / 1000, 2)
    logger.info(f"Water dispensed: {dispensed_liters} L")

    balance -= dispensed_liters
    balance = max(balance, 0)

    result_msg = json.dumps({
        "dispensed": dispensed_liters,
        "updated_balance": round(balance, 2)
    })

    if client.is_connected():
        client.publish(TOPIC_PUB_RESULT, result_msg, qos=0, retain=False)
        logger.info(f"Sent result to server: {result_msg}")
    else:
        logger.error("MQTT disconnected — skipping result publish")

# -------------------------------------------------------------------
# Main Function
# -------------------------------------------------------------------
def main():
    global current_card_uid

    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, clean_session=True)
    client.max_queued_messages_set(0)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    try:
        client.connect(BROKER, PORT, keepalive=10)
    except Exception as e:
        logger.error(f"Could not connect to broker: {e}")
        return

    client.loop_start()

    try:
        while True:
            try:
                uid, _ = reader.read()
                if uid != current_card_uid:
                    current_card_uid = uid
                    message = json.dumps({"uid": str(uid)})
                    logger.info(f"Publishing UID: {uid} to topic: {TOPIC_PUB_UID}")
                    if client.is_connected():
                        result = client.publish(TOPIC_PUB_UID, message, qos=0, retain=False)
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logger.info("UID published successfully")
                        else:
                            logger.warning(f"Failed to publish UID. Status: {result.rc}")
                    else:
                        logger.error("MQTT disconnected — skipping publish")
            except Exception:
                current_card_uid = None  # Reset if card is not readable
            time.sleep(1)
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
