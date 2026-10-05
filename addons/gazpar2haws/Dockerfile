ARG BUILD_FROM
FROM $BUILD_FROM

# Gazpar2HAWS version to install
ARG GAZPAR2HAWS_VERSION

# Install Python 3 and required system packages
# - python3: Latest Python 3.x runtime available in Alpine 3.23 (likely 3.12)
# - py3-pip: Python package manager
# - gettext: Provides envsubst command for configuration templating
# - yq: YAML processor for configuration file manipulation
RUN apk add --no-cache \
        python3 \
        py3-pip \
        gettext \
        yq

# Allow pip to install packages system-wide (required for Python 3.11+)
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install gazpar2haws from PyPI only: TestPyPI is not an index here, as a same-named package there could be picked up
RUN pip3 install --no-cache-dir gazpar2haws==${GAZPAR2HAWS_VERSION}

WORKDIR /app

# Copy addon files and set executable permissions
COPY rootfs /
RUN chmod +x /app/run.sh && \
    chmod +x /etc/services.d/gazpar2haws/run && \
    chmod +x /etc/services.d/gazpar2haws/finish
