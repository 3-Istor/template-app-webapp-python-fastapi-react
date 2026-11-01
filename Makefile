.PHONY: install check migrate migration

# Agents run each command in a fresh shell, so use the venv's python directly.
PYTHON := $(if $(wildcard backend/.venv/bin/python),.venv/bin/python,python3)

install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
	cd frontend && npm install

check:
	cd backend && $(PYTHON) -m pytest -q
	cd frontend && npm run build

migrate:
	docker compose run --rm migrate

migration:
	@test -n "$(name)" || { echo 'usage: make migration name="add email_verified"'; exit 1; }
	docker compose run --rm -e MIGRATION_NAME="$(name)" migrate \
		sh -c '/app/migrate && alembic revision --autogenerate -m "$$MIGRATION_NAME"'
