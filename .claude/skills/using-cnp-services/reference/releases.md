# Releases, staging and canary

## Cutting a release

- Tag `main` with `vX.Y.Z`, from the CMP Release tab, from the `cnp` tool
  `cut_release` (`patch`, `minor` or `major`), or with
  `git tag vX.Y.Z && git push origin vX.Y.Z`.
- CI builds both images under `X.Y.Z`. If a tag already exists, CI refuses to
  rebuild it: push the next version (or `-rc.N`) instead of moving the tag.
- Before the new pods start, the platform takes a backup (when backups are on)
  and runs the migration Job. A migration that fails stops the release, and
  the running version stays.
- Follow a rollout from the CMP Release tab or with the `cnp-release` skill of
  the `cnp` plugin. From there you can promote it step by step, retry a failed
  check, or abort it, which sends all traffic back to the stable version.

## Staging

When staging is turned on for the app in the CMP:

- Each version lands first on `https://<app>-<project>-staging.3istor.com`. It
  runs in the namespace `<namespace>-stg`, with its own database, SSO client
  and secrets (`<app>/staging` in Vault).
- The CMP then promotes it to prod in this order: smoke check, the app's
  verification suites, soak time, and an admin's approval when the project's
  policy requires one. It commits the prod image to `deploy/env/prod/`.
- A verification suite of kind "external" is a workflow of this repository
  started with `workflow_dispatch`, by default `.github/workflows/cnp-verify.yml`.
  It receives `target_url` and must post its result to `callback_url`. Put real
  checks (API calls, end-to-end tests) in its "Run the tests" step.

## Canary

- Only the frontend can run a canary, because a canary shifts traffic on the
  app's HTTP route and the backend has none. The CMP refuses it on the backend.
- Turn it on and pick a preset (`safe`, `fast`, `demo`, `manual`) in the CMP
  Release tab. The CMP writes `release:` in `values-frontend.yaml`, including
  the smoke path.
- A canary runs two versions at once against the same database. The migration
  rules in `.claude/rules/migrations.md` are what make that safe.
- Sticky cookies keep each user on the version that served them first, so the
  old and new frontends must both work with the backend in place during the
  rollout.
