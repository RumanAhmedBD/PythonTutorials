#!/usr/bin/env python3

## @file read_mac_addr.py
#  @brief Retrieves MAC address and formats MQTT client ID and topic for Water ATM

import os
import logging

# ------------------------------------------------------------------------------
# Setup logger
# ------------------------------------------------------------------------------

## @brief Module-level logger for ATM device-related operations
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)

# Configure logging output format and handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ------------------------------------------------------------------------------
# MAC Address Utilities
# ------------------------------------------------------------------------------

## @brief Reads the MAC address from a given network interface.
#  @param interface Name of the network interface (e.g., "eth0", "wlan0")
#  @return MAC address string in standard format (e.g., "dc:a6:32:1e:12:34") or None if not found
def get_mac(interface='eth0'):
    try:
        with open(f'/sys/class/net/{interface}/address') as f:
            mac = f.read().strip()
            logger.debug(f"MAC address from {interface}: {mac}")
            return mac
    except FileNotFoundError:
        logger.error(f"Interface {interface} not found.")
        return None

## @brief Formats a MAC address into a lowercase, MQTT-safe string (removes colons).
#  @param mac The MAC address in standard format
#  @return Formatted MAC string (e.g., "dca6321e1234")
def format_mac_for_id(mac):
    formatted = mac.replace(":", "").lower() if mac else "unknown"
    logger.debug(f"Formatted MAC for ID: {formatted}")
    return formatted

# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------

## @brief Main function to retrieve MAC, format it, and display MQTT client ID and topic.
def main():
    logger.info("Starting MAC address identification...")

    mac = get_mac('eth0')  # Don?t want fallback for now
    if not mac:
        logger.error("Could not find MAC address.")
        return

    device_id = format_mac_for_id(mac)
    mqtt_client_id = f"atm-{device_id[-6:]}"  # Use last 6 chars
    mqtt_topic = f"water_atm/{device_id}"

    logger.info(f"MAC Address: {mac}")
    logger.info(f"MQTT Client ID: {mqtt_client_id}")
    logger.info(f"MQTT Topic: {mqtt_topic}")

## @brief Entry point of the script
if __name__ == "__main__":
    main()
