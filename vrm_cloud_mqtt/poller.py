"""Poller."""

import json
import logging
from time import sleep

from vrm_cloud_mqtt.config import settings
from vrm_cloud_mqtt.mqtt import MqttClient
from vrm_cloud_mqtt.vrm import VrmLogin, VrmSite

logger = logging.getLogger("poller")


def poll_vrm(vrm: VrmLogin) -> dict:
    """Poll the Vrm."""
    data = {}

    sites = vrm.get_sites()

    for site in sites:
        msg = f"Polling site {site.site_id}"
        logger.info(msg)
        devices = site.get_devices()
        data[site.site_id] = devices

    return data


def run_interval(vrm: VrmLogin, mqtt_client: MqttClient) -> None:
    """Run the polling interval."""
    site_data = poll_vrm(vrm)

    for site_id, devices in site_data.items():
        for device in devices:
            mqtt_client.publish(json.dumps(devices[device]), f"site/{site_id}/{device}")


def start_polling(vrm: VrmLogin, mqtt_client: MqttClient) -> None:
    """Start polling."""
    msg = f"Polling interval: {settings.poll_interval} seconds"
    logger.info(msg)

    try:
        while True:
            run_interval(vrm, mqtt_client)
            sleep(settings.poll_interval)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping polling")
        mqtt_client.stop()
