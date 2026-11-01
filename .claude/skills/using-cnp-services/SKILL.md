---
name: using-cnp-services
description: Explains how this app uses the CNP platform services, namely PostgreSQL and its backups, secrets from Vault, company SSO and the logged-in user, releases with staging and canary, logs, monitoring and off-hours sleep. Use when a task touches the database, configuration or secrets, login, user identity or access rights, deployment or releases, logs, or a file in deploy/.
user-invocable: false
---

# Using the CNP services from this app

The platform renders `deploy/values-backend.yaml` and
`deploy/values-frontend.yaml` with its generic Helm chart. A key changed in
those files reaches the cluster at the next sync of `main`; nothing is changed
on the cluster by hand. Each service below says what the app gets, what the
code does with it, and where it is switched on or off.

## PostgreSQL

- On by default: `db.enabled: true` in `values-backend.yaml`. It is a CloudNativePG
  cluster with one instance and `db.storage` of disk (1Gi).
- The backend receives `DB_TYPE=postgres`, `DB_HOST`, `DB_PORT`, `DB_NAME`,
  `DB_USER` and `DB_PASSWORD`. `Settings.database_url` builds the URL from
  them, so no code change is needed.
- Locally the backend uses SQLite (`backend/app.db`). For PostgreSQL, run
  `docker compose --profile postgres up` with `DB_TYPE=postgres` in `.env`.
- Schema changes are Alembic revisions only; see `.claude/rules/migrations.md`.
- Projects on AWS or GCP keep the database on the node's local disk (storage
  class `local-path`). The data does not survive losing the node or the cluster.

## Backups and restore

- Off by default, because storage is scarce. Turn them on in the CMP or with
  `db.backup.enabled: true`. The defaults are a daily backup at 03:00 kept 7
  days (`db.backup.schedule`, `db.backup.retentionPolicy`).
- With backups on, every release takes a backup before it migrates.
- Restores are done with the CMP's restore button, which writes `db.restore`.
  Never edit `db.restore` by hand.

## Secrets and configuration

- Secrets live in Vault under the app's path. The platform turns every key into
  an environment variable of both pods, read when a pod starts. A new or
  changed value reaches the app at the next rollout.
- To add a secret, the user enters the value in the CMP (app › Config tab).
  From an agent, call the `cnp` tool `request_secret`, which gives the user the
  link. Never ask for the value in the conversation, and never write it to a
  file or a commit.
- Name keys in UPPER_SNAKE_CASE, then declare a field in `Settings`:
  `stripe_key: str = ""` reads `STRIPE_KEY`. The keys `username`, `password`
  (database) and `client-secret` (SSO) are the platform's own; leave them alone.
- Configuration that is not secret goes in `env:` in `values-backend.yaml`,
  with a default in `Settings` for local runs.

## SSO and the logged-in user

- Every app sits behind the company login (Keycloak, realm = project name).
  Who may open it is the app's exposure setting in the CMP. Its four presets
  write `ingress.sso_protected` and `ingress.allowedGroups` in
  `values-frontend.yaml`:
  - `public`: no login
  - `project users`: any account in the project realm (the default)
  - `project members`: groups `project-members` and `project-admins`
  - `project admins`: group `project-admins`
- The backend only learns who the user is with `project members` or
  `project admins`. With either, the gateway forwards the access token as
  `Authorization: Bearer <JWT>`. Reading it and checking roles:
  [reference/identity.md](reference/identity.md).
- Logout is `/logout` on the app's URL.

## Releases, staging and canary

A release is a `vX.Y.Z` tag on `main`. CI publishes `backend:X.Y.Z` and
`frontend:X.Y.Z`, and the platform rolls them out. For staging, promotion,
canary and verification suites, see [reference/releases.md](reference/releases.md).

## Health, monitoring and logs

- The status page probes `monitoring.path`: `/health` for the backend, `/` for
  the frontend. Keep `/health` cheap and unauthenticated.
- Logs are collected from stdout. Use the standard `logging` module with one
  line per event, and never log secrets, tokens or personal data. Read logs
  with the `cnp` tool `get_app_logs` or in the CMP. Retention is 14 days by
  default (`logRetention`: `7d`, `14d` or `30d`).

## Off-hours

- `offhours.enabled: true` in both values files scales the app to zero from
  `sleepAt` to `wakeAt` (01:00 to 07:00 Europe/Paris). The database stays up.
- A visitor during that window sees a sleeping page. A sync from the CMP wakes
  the app early.
- Work that must run on a schedule cannot live in the pod. Ask the platform
  team before designing one.

## Security scans

Every push runs secret scanning (gitleaks) and Trivy on the dependencies, the
Dockerfiles and the built images. Alerts go to the project's Discord when it
has one. The CMP sets whether findings block CI (`deploy/security.yaml`).
Dependabot opens weekly update PRs and auto-merges patch and minor bumps,
except for packages still on 0.x.
