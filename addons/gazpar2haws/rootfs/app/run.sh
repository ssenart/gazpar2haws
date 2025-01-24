#!/usr/bin/with-contenv bashio

# Load the Add-on configuration in JSON and reformat it to YAML.
GRDF_JSON="{ 'grdf': $(bashio::addon.config) }"
GRDF_CONFIG=$(echo $GRDF_JSON | yq -P)

# Home Assistant configuration for Add-on
HOMEASSISTANT_HOST=supervisor
HOMEASSISTANT_PORT=80
HOMEASSISTANT_ENDPOINT=/core/websocket
HOMEASSISTANT_TOKEN=${SUPERVISOR_TOKEN}

# Display environment variables
bashio::log.info "GRDF_CONFIG: ${GRDF_CONFIG}"
bashio::log.info "HOMEASSISTANT_HOST: ${HOMEASSISTANT_HOST}"
bashio::log.info "HOMEASSISTANT_PORT: ${HOMEASSISTANT_PORT}"
bashio::log.info "HOMEASSISTANT_ENDPOINT: ${HOMEASSISTANT_ENDPOINT}"
bashio::log.info "HOMEASSISTANT_TOKEN: ${HOMEASSISTANT_TOKEN}"

# Export environment variables
export GRDF_CONFIG HOMEASSISTANT_HOST HOMEASSISTANT_PORT HOMEASSISTANT_ENDPOINT HOMEASSISTANT_TOKEN

# Instantiate the template config
if [ ! -e /app/config/configuration.yaml ]; then
    envsubst < "/app/config/configuration.template.yaml" > "/app/config/configuration.yaml"
fi

# Display the configuration file: Uncomment below for debugging
# echo "Configuration file:"
# cat /app/config/configuration.yaml

# Run the gazpar2haws python program
cd /app

python3 -m gazpar2haws --config config/configuration.yaml --secrets config/secrets.yaml
