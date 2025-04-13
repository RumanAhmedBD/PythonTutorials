"""
A complete MQTT pub-sub client using paho-mqtt for the Water ATM system.
This script simulates reading an NFC card UID, handles server authentication
through MQTT messages, and simulates water dispensing with flow sensor feedback.

Author: Ruman Ahmed
"""

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import uuid
import json
import logging
import ssl
import random

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
BROKER = "broker.emqx.io"  # Public broker (use your own for production)
PORT = 8883  # TLS port

DEVICE_ID = uuid.getnode()
DEVICE_ID_STR = f"atm-{DEVICE_ID:012x}"
TOPIC_PUB_UID = f"water_atm/{DEVICE_ID_STR}/uid"
TOPIC_PUB_RESULT = f"water_atm/{DEVICE_ID_STR}/result"
TOPIC_SUB_AUTH = f"water_atm/{DEVICE_ID_STR}/auth"
TOPIC_SUB_CONFIRM = f"water_atm/{DEVICE_ID_STR}/confirm"

authenticated = False
balance = 0

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
                dispense_water(client)
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
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    if reason_code == mqtt.MQTT_ERR_SUCCESS:
        logger.info("Disconnected cleanly from MQTT broker")
        return

    logger.warning("Disconnected unexpectedly from MQTT broker")
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
# Simulate NFC UID read
# -------------------------------------------------------------------
def simulate_nfc_uid():
    return uuid.uuid4().hex[:8]  # Simulated UID

# -------------------------------------------------------------------
# Simulate water dispensing and flow sensor
# -------------------------------------------------------------------
def dispense_water(client):
    global balance
    logger.info("Starting water dispensing...")

    total_pulses = 0
    duration = 5
    start_time = time.time()

    while time.time() - start_time < duration:
        pulses = random.randint(1, 5)
        total_pulses += pulses
        time.sleep(0.2)

    water_dispensed_ml = total_pulses * 2
    water_dispensed_liters = round(water_dispensed_ml / 1000, 2)

    logger.info(f"Water dispensed: {water_dispensed_liters} L")
    balance -= water_dispensed_liters
    balance = max(balance, 0)

    message = json.dumps({
        "dispensed": water_dispensed_liters,
        "updated_balance": round(balance, 2)
    })

    if client.is_connected():
        result = client.publish(TOPIC_PUB_RESULT, message, qos=0, retain=False)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Sent result to server: {message}")
        else:
            logger.warning("Publish failed")
    else:
        logger.error("MQTT disconnected — skipping publish")

# -------------------------------------------------------------------
# Main Function
# -------------------------------------------------------------------
def main():
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, clean_session=True)
    client.max_queued_messages_set(0)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Could not connect to broker: {e}")
        return

    client.loop_start()

    try:
        while True:
            if not authenticated:
                uid = simulate_nfc_uid()
                message = json.dumps({"uid": uid})
                logger.info(f"Publishing UID: {uid} to topic: {TOPIC_PUB_UID}")
                if client.is_connected():
                    result = client.publish(TOPIC_PUB_UID, message, qos=0, retain=False)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info("UID published successfully")
                    else:
                        logger.warning(f"Failed to publish UID. Status: {result.rc}")
                else:
                    logger.error("MQTT disconnected — skipping publish")
            time.sleep(10)
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