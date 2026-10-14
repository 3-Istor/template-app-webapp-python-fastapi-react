.PHONY: migrate migration

migrate:
	docker compose run --rm migrate

migration:
	@test -n "$(name)" || { echo 'usage: make migration name="add email_verified"'; exit 1; }
	docker compose run --rm -e MIGRATION_NAME="$(name)" migrate \
		sh -c '/app/migrate && alembic revision --autogenerate -m "$$MIGRATION_NAME"'
