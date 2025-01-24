# The builder image, used to build the virtual environment
ARG BUILD_FROM
FROM $BUILD_FROM

# Gazpar2HAWS version to install.
ARG GAZPAR2HAWS_VERSION

RUN apk add --no-cache gettext
RUN apk add --no-cache yq

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN pip3 install --no-cache-dir gazpar2haws==${GAZPAR2HAWS_VERSION}

WORKDIR /app

COPY rootfs /
RUN  chmod +x /app/run.sh
RUN  chmod +x /etc/services.d/gazpar2haws/run
RUN  chmod +x /etc/services.d/gazpar2haws/finish
