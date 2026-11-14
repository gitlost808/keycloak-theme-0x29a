FROM quay.io/keycloak/keycloak:26.8.2@sha256:3879c623248408de29a5303178b5816c77e8dfef3890c361f8c0bbeaa979ba3b
LABEL org.opencontainers.image.source="https://github.com/gitlost808/keycloak-theme-0x29a"
COPY --chown=1000:0 theme/0x29a/ /opt/keycloak/themes/0x29a/
