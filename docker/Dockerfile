# The builder image, used to build the virtual environment
FROM python:3.12-bookworm AS builder

RUN pip install uv==0.13.0

# The virtual environment is created in /app/.venv with the Python of the image, from the locked versions.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./
COPY LICENSE ./

COPY gazpar2haws/ /app/gazpar2haws

RUN cat pyproject.toml | grep "^version = " | awk '{print $3}' | tr -d '"' > /app/VERSION

RUN uv sync --locked --no-dev
RUN cat /app/VERSION

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm AS runtime

# Environment variables
# GRDF_USERNAME: The username to use to authenticate to the GRDF API
# GRDF_PASSWORD: The password to use to authenticate to the GRDF API
# GRDF_PCE_IDENTIFIER: The identifier of the PCE to use to fetch the data
# GRDF_SCAN_INTERVAL: The interval in minutes between two scans of the GRDF API
# GRDF_LAST_DAYS: The number of days to fetch when fetching the data
# HOMEASSISTANT_HOST: The hostname of the Home Assistant instance
# HOMEASSISTANT_PORT: The port of the Home Assistant instance
# HOMEASSISTANT_ENDPOINT: The endpoint to use to send the data to the Home Assistant
# HOMEASSISTANT_TOKEN: The long-lived access token to use to authenticate to the Home Assistant instance

# Install the required system dependencies: envsubst
RUN apt-get update && apt-get install -y gettext-base

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app/VERSION /app/VERSION

RUN cat /app/VERSION

COPY docker/entrypoint.sh /app
RUN  chmod +x /app/entrypoint.sh
COPY gazpar2haws/ /app/gazpar2haws
RUN  mkdir /app/config
RUN  mkdir /app/log
COPY README.md /app
COPY CHANGELOG.md /app
COPY LICENSE /app
COPY config/configuration.template.yaml /app
COPY config/secrets.template.yaml /app

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
