# Makefile

.PHONY: dev debug

dev:
	export PYTHONDONTWRITEBYTECODE=1; \
	uv run --package web-service fastapi dev apps/web-service/app/main.py --port 8080

debug:
	export PYTHONDONTWRITEBYTECODE=1; \
	uv run --package web-service python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m fastapi dev apps/web-service/app/main.py --port 8000