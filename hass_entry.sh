#!/usr/bin/with-contenv bashio


export VRM_MQTT_HOST=$(bashio::config 'mqtt_host' $(bashio::services mqtt "host" " "))
export VRM_MQTT_PORT=$(bashio::config 'mqtt_port' $(bashio::services mqtt "port" " "))
export VRM_MQTT_USERNAME=$(bashio::config 'mqtt_username' $(bashio::services mqtt "username" " "))
export VRM_MQTT_PASSWORD=$(bashio::config 'mqtt_password' $(bashio::services mqtt "password" " "))
export VRM_MQTT_TOPIC=$(bashio::config 'mqtt_topic')

export VRM_USERNAME=$(bashio::config 'vrm_username')
export VRM_PASSWORD=$(bashio::config 'vrm_password')
export VRM_SITE_ID=$(bashio::config 'vrm_site_id')
export VRM_POLL_INTERVAL=$(bashio::config 'vrm_poll_interval')
export VRM_TOKEN_NAME=$(bashio::config 'vrm_token_name')
export VRM_DEBUG=$(bashio::config 'vrm_debug')


  uv run run_poller.py
