"""Main module for the Vrm API."""

import logging

from vrm_cloud_mqtt import MqttClient, VrmLogin, start_polling
from vrm_cloud_mqtt.config import settings

# Configure logging based on debug setting
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Log the current logging level
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to: {logging.getLevelName(log_level)}")


if __name__ == "__main__":
    mqtt_client = MqttClient(
        host=settings.mqtt_host,
        port=settings.mqtt_port,
        topic=settings.mqtt_topic,
        username=settings.mqtt_username,
        password=settings.mqtt_password,
    )
    mqtt_client.run()
    vrm = VrmLogin(settings.username, settings.password)

    if vrm.token is None:
        vrm.login()

    start_polling(vrm, mqtt_client)
