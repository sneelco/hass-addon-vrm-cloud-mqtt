# Configuration

This application uses environment variables for configuration. You can set these in several ways:

## Option 1: Create a .env file

Create a `.env` file in the project root with the following content:

```bash
# VRM Cloud MQTT Configuration
VRM_USERNAME=your_username_here
VRM_PASSWORD=your_password_here
```

## Option 2: Set environment variables directly

```bash
export VRM_USERNAME=your_username_here
export VRM_PASSWORD=your_password_here
```

## Option 3: Set when running the application

```bash
VRM_USERNAME=your_username_here VRM_PASSWORD=your_password_here python main.py
```

## Configuration Keys

- `VRM_USERNAME`: Username for authentication
- `VRM_PASSWORD`: Password for authentication
- `VRM_ID_SITE`: ID of the site
- `VRM_TOKEN_NAME`: Name of the token (default: "vrm-cloud-mqtt")
- `VRM_REVOKE_DUPLICATE_TOKEN`: Whether to revoke duplicate tokens (default: false)
- `VRM_MQTT_HOST`: MQTT broker hostname or IP address
- `VRM_MQTT_PORT`: MQTT broker port (default: 1883)
- `VRM_MQTT_TOPIC`: MQTT topic prefix (default: "vrm/cloud")
- `VRM_MQTT_USERNAME`: MQTT broker username (optional)
- `VRM_MQTT_PASSWORD`: MQTT broker password (optional)
- `VRM_POLL_INTERVAL`: Poll interval in seconds (default: 60)
- `VRM_DEBUG`: Enable debug logging (default: false)

## Cache File

The application automatically caches authentication data to a `.cache` file in the project root. This file:
- Stores the authentication token and user ID after successful login
- Is automatically loaded when the `Login` class is instantiated
- Contains sensitive data and should not be committed to version control

**Note**: Add `.cache` to your `.gitignore` file to prevent accidentally committing tokens.

## Logging

The application uses Python's built-in logging module with the following configuration:
- **Log Level**: INFO (shows informational messages, warnings, and errors)
- **Output**: Both console (stdout) and file (`vrm.log`)
- **Format**: Timestamp, logger name, log level, and message
- **Log File**: `vrm.log` in the project root

**Note**: Add `vrm.log` to your `.gitignore` file to prevent accidentally committing log files.

## Installation

Install the required dependencies:

```bash
pip install -e .
```

## Usage

The application will automatically load configuration from environment variables or a `.env` file when you run:

```bash
python main.py
```

On first run, you'll need to authenticate. Subsequent runs will use the cached token automatically.
