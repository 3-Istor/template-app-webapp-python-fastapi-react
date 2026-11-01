---
paths:
  - "backend/app/models.py"
  - "backend/app/models/**"
  - "backend/migrations/**"
---

# Changing the database schema

1. Change the models, then run `make migration name="<what changes>"`.
2. Read the generated revision. Autogenerate reads a rename as a drop plus an
   add, and misses some type and server-default changes.
3. The previous release runs on the new schema until the rollout ends. Split
   anything it would break across releases:
   - New table, nullable column or column with a default: one release.
   - Index: one release, with `postgresql_concurrently=True` inside
     `op.get_context().autocommit_block()`.
   - Making a column required, or dropping a column or table: two releases.
     First the code stops depending on it, then the schema changes.
   - Renaming a column or changing its type: three releases. Add the new
     column, write both and backfill; then read the new one; then drop the old.
4. The revision that finishes a split declares the squawk rule it expects to
   break at module level, for example `squawk_ignore = ["ban-drop-column"]`.
   CI runs squawk on the PostgreSQL SQL of every new revision. A migration that
   really breaks the running version needs the `migration:breaking` PR label,
   and a project admin approves it at release time.
5. No heavy data work in a migration: the Job is killed after
   `migrations.timeout` (5 min by default). Backfill from the app, in batches.
6. Never edit a revision that is already on `main`, and never count on a
   downgrade in prod. Fix forward with a new revision.
7. Check: `make check` runs `app/test_migrations.py` (upgrade to head, twice).
   `docker compose up` applies the migration locally.
