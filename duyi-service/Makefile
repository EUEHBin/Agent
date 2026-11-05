# Makefile

.PHONY: dev debug test test-unit test-integration test-e2e test-smoke test-html test-changed db-migrate db-upgrade db-downgrade

dev:
	export PYTHONDONTWRITEBYTECODE=1; \
	uv run --package web-service fastapi dev apps/web-service/app/main.py --port 8080

debug:
	export PYTHONDONTWRITEBYTECODE=1; \
	uv run --package web-service python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m fastapi dev apps/web-service/app/main.py --port 8000

test:
	COVERAGE_FILE=.coverage.duyi \
	  uv run pytest packages/duyi-utils/test/ -q \
	    --cov=duyi_utils --cov-report=html:htmlcov/duyi-utils --cov-fail-under=80 && \
	COVERAGE_FILE=.coverage.web \
	  uv run pytest apps/web-service/test/unit/ apps/web-service/test/integration/ -q \
	    --cov=app --cov-report=html:htmlcov/web-service --cov-fail-under=80

test-unit:
	uv run pytest packages/duyi-utils/test/unit/ apps/web-service/test/unit/ -q

test-integration:
	uv run pytest packages/duyi-utils/test/integration/ apps/web-service/test/integration/ -q

test-e2e:
	uv run pytest apps/web-service/test/e2e/ -q

test-smoke:
	uv run pytest apps/web-service/test/e2e/ -q -m smoke
	uv run pytest packages/duyi-utils/test/ apps/web-service/test/integration/ -q -m smoke

test-changed:
	uv run python scripts/run_changed_tests.py

db-migrate:
	uv run --package web-service alembic -c apps/web-service/alembic.ini revision --autogenerate -m "$(message)"

db-upgrade:
	uv run --package web-service alembic -c apps/web-service/alembic.ini upgrade head

db-downgrade:
	uv run --package web-service alembic -c apps/web-service/alembic.ini downgrade $(version)
