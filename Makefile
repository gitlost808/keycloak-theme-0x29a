.PHONY: test test-image

IMAGE ?= keycloak-theme-0x29a:local

test:
	python3 -m unittest discover -s tests -v

test-image:
	docker build --tag "$(IMAGE)" .
	python3 scripts/check-image.py "$(IMAGE)"
