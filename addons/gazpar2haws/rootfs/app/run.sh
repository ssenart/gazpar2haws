#!/usr/bin/with-contenv bashio

# Location of the Add-on configuration file
CONFIG_PATH=/data/options.json

# Load the Add-on configuration in JSON and reformat it to YAML.
SCAN_INTERVAL_JSON=$(jq --raw-output '.scan_interval // empty' $CONFIG_PATH)

DEVICES_JSON=$(jq --raw-output '.devices // empty' $CONFIG_PATH)

GRDF_JSON="{ 'grdf': { 'scan_interval': $SCAN_INTERVAL_JSON, 'devices': $DEVICES_JSON } }"

GRDF_CONFIG=$(echo $GRDF_JSON | yq -P)

VAT_JSON=$(jq --raw-output '.vat // empty' $CONFIG_PATH)

CONSUMPTION_PRICES_JSON=$(jq --raw-output '.consumption_prices // empty' $CONFIG_PATH)

SUBSCRIPTION_PRICES_JSON=$(jq --raw-output '.subscription_prices // empty' $CONFIG_PATH)

TRANSPORT_PRICES_JSON=$(jq --raw-output '.transport_prices // empty' $CONFIG_PATH)

ENERGY_TAXES_JSON=$(jq --raw-output '.energy_taxes // empty' $CONFIG_PATH)

PRICING_JSON="{ 'pricing': { 'vat': $VAT_JSON , 'consumption_prices': $CONSUMPTION_PRICES_JSON, 'subscription_prices': $SUBSCRIPTION_PRICES_JSON, 'transport_prices': $TRANSPORT_PRICES_JSON, 'energy_taxes': $ENERGY_TAXES_JSON } }"

PRICING_CONGIG=$(echo $PRICING_JSON | yq -P)

# Home Assistant configuration for Add-on
HOMEASSISTANT_HOST=supervisor
HOMEASSISTANT_PORT=80
HOMEASSISTANT_ENDPOINT=/core/websocket
HOMEASSISTANT_TOKEN=${SUPERVISOR_TOKEN}

# Display environment variables
bashio::log.info "GRDF_CONFIG: ${GRDF_CONFIG}"
bashio::log.info "PRICING_CONGIG: ${PRICING_CONGIG}"
bashio::log.info "HOMEASSISTANT_HOST: ${HOMEASSISTANT_HOST}"
bashio::log.info "HOMEASSISTANT_PORT: ${HOMEASSISTANT_PORT}"
bashio::log.info "HOMEASSISTANT_ENDPOINT: ${HOMEASSISTANT_ENDPOINT}"
bashio::log.info "HOMEASSISTANT_TOKEN: ${HOMEASSISTANT_TOKEN}"

# Export environment variables
export GRDF_CONFIG PRICING_CONGIG HOMEASSISTANT_HOST HOMEASSISTANT_PORT HOMEASSISTANT_ENDPOINT HOMEASSISTANT_TOKEN

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
