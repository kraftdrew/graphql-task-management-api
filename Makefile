DEV_COMPOSE := docker compose
PROD_COMPOSE := docker compose -f compose.yaml
TEST_COMPOSE := docker compose -f compose.test.yaml
UV := uv

.PHONY: run-prod run-dev run-dev-clean-db stop test

run-prod:
	$(PROD_COMPOSE) up -d --build --wait

run-dev:
	$(DEV_COMPOSE) up -d --build --wait
	@echo "GraphiQL example: http://localhost:8000/example"

run-dev-clean-db:
	$(DEV_COMPOSE) down --volumes
	$(DEV_COMPOSE) up -d --build --wait
	@echo "GraphiQL example: http://localhost:8000/example"

stop:
	$(DEV_COMPOSE) down

run-tests:
	@set -e; \
	cleanup() { $(TEST_COMPOSE) down; }; \
	trap cleanup EXIT; \
	$(TEST_COMPOSE) up -d --wait; \
	$(UV) run --extra dev pytest -v
