#!/bin/sh

# Check/Set default values to optional environment variables
: "${GRDF_USERNAME:?GRDF_USERNAME is required and not set.}"
: "${GRDF_PASSWORD:?GRDF_PASSWORD is required and not set.}"
: "${GRDF_PCE_IDENTIFIER:?GRDF_PCE_IDENTIFIER is required and not set.}"
: "${GRDF_SCAN_INTERVAL:="480"}" # 8 hours
: "${GRDF_LAST_DAYS:="1095"}" # 3 years

: "${HOMEASSISTANT_HOST:?HOMEASSISTANT_HOST is required and not set.}"
: "${HOMEASSISTANT_PORT:="8123"}" # Default Home Assistant port
: "${HOMEASSISTANT_ENDPOINT:="/api/websocket"}" # Default Home Assistant endpoint
: "${HOMEASSISTANT_TOKEN:?HOMEASSISTANT_TOKEN is required and not set.}"

# Display environment variables
echo "GRDF_USERNAME: ${GRDF_USERNAME}"
echo "GRDF_PASSWORD: ***************"
echo "GRDF_PCE_IDENTIFIER: ${GRDF_PCE_IDENTIFIER}"
echo "GRDF_SCAN_INTERVAL: ${GRDF_SCAN_INTERVAL}"
echo "GRDF_LAST_DAYS: ${GRDF_LAST_DAYS}"
echo "HOMEASSISTANT_HOST: ${HOMEASSISTANT_HOST}"
echo "HOMEASSISTANT_ENDPOINT: ${HOMEASSISTANT_ENDPOINT}"
echo "HOMEASSISTANT_PORT: ${HOMEASSISTANT_PORT}"
echo "HOMEASSISTANT_TOKEN: ***************"

# Export environment variables
export GRDF_USERNAME GRDF_PASSWORD GRDF_PCE_IDENTIFIER GRDF_SCAN_INTERVAL GRDF_LAST_DAYS HOMEASSISTANT_HOST HOMEASSISTANT_PORT HOMEASSISTANT_ENDPOINT HOMEASSISTANT_TOKEN

# Instantiate the template config
if [ ! -e /app/config/configuration.yaml ]; then
    envsubst < "/app/configuration.template.yaml" > "/app/config/configuration.yaml"
fi

# Instantiate the template secrets
if [ ! -e /app/config/secrets.yaml ]; then
    envsubst < "/app/secrets.template.yaml" > "/app/config/secrets.yaml"
fi

# Run the gazpar2haws python program
cd /app
python3 -m gazpar2haws
