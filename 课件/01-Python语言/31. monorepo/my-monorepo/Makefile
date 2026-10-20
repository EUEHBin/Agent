.PHONY: run-web build

run-web:
	uv run --package web-service python app/web-service/main.py

build:
	uv build --package shared
	uv build --package agents