# Reading the logged-in user in the backend

The gateway's OIDC filter logs the user in. In every exposure but `public`
(`ingress.sso_protected: true` in `deploy/values-frontend.yaml`), it also
forwards the access token to nginx as `Authorization: Bearer <JWT>`, and nginx
passes it on to `/api/*`. A non-empty `ingress.allowedGroups` (`project members`
or `project admins`) adds a check of the token and of the group at the gateway.
`project users` lets in any account of the realm, customers included, so check
`groups` in the backend for staff-only routes. With `public`, no identity
reaches the backend.

Verify the token in the backend anyway. Every pod of the project, and a few
platform namespaces, can reach the backend Service without going through the
gateway, so a header on its own proves nothing. Check the signature (realm
JWKS) and the issuer. The issuer depends on the environment:

| Environment | Issuer |
|---|---|
| prod | `https://auth.3istor.com/realms/<project>` |
| staging | `https://auth.3istor.com/realms/<project>-staging` |

`<project>` is `project_name` in `deploy/values-backend.yaml`. A project with
its own Keycloak uses `https://auth-<project>.3istor.com/realms/<realm>`.
Staging users live in their own realm, so a prod issuer rejects every staging
login: never hard-code it.

1. Pin `PyJWT[crypto]` in `backend/requirements.txt`.
2. Add `oidc_issuer: str = ""` to `Settings`, and set `OIDC_ISSUER` under `env:`
   in `deploy/values-backend.yaml` (prod). Staging sets its own value in
   `deploy/env/staging/backend.yaml`. Helm replaces a list instead of merging
   it, so that file's `env:` must repeat every variable the backend needs.
3. Add a dependency, for example in `app/security.py`:

```python
from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException

from app.config import get_settings


@lru_cache
def _jwks() -> jwt.PyJWKClient:
    issuer = get_settings().oidc_issuer
    return jwt.PyJWKClient(f"{issuer}/protocol/openid-connect/certs")


def current_user(authorization: str = Header(default="")) -> dict:
    token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="Not signed in")
    try:
        key = _jwks().get_signing_key_from_jwt(token).key
        # Keycloak access tokens carry aud "account"; azp is the app's client.
        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=get_settings().oidc_issuer,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_group(group: str):
    def check(user: dict = Depends(current_user)) -> dict:
        if group not in user.get("groups", []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return check
```

4. Use it in routes: `user: dict = Depends(current_user)`. Store
   `user["sub"]` as the owner of a row. It is the stable user id; the e-mail
   address and username can change.
5. In tests, override the dependency instead of minting tokens:
   `app.dependency_overrides[current_user] = lambda: {"sub": "u1", "groups": ["project-members"]}`.
   `docker compose` runs without the gateway, so signed-in routes answer 401
   locally. The tests cover them, and staging checks the real login.

Useful claims: `sub`, `preferred_username`, `email`, `name`, and `groups`
(`project-members`, `project-admins`; `users` for customers). Group names come
without a leading slash, as `ingress.allowedGroups` expects them.

## Public paths

A path reachable without login (a webhook, a device endpoint) is listed in
`ingress.publicPaths` of `deploy/values-frontend.yaml`:
`[{path: /api/v1/telemetry, method: POST}]`. No login also means no token:
the endpoint authenticates the caller itself (API key, signature).

- `match` is `Exact` unless you ask for `PathPrefix`; no `method` means all
  methods. `/api/v1/telemetry/` does not match `/api/v1/telemetry`.
- `path` starts with `/`. `/` as a prefix is refused: for a public app, pick
  the `public` exposure.
- During a canary, public paths only reach the stable version.

## Customer sign-up and organizations

Off by default. A project admin turns it on in the CMP (project "..." menu,
"Customer sign-up"); an assistant cannot (403). When on:

- The prod realm opens registration. Customers land in group `users`, never in
  `project-members`. No e-mail is sent: no verification, no invitation. The
  staging realm never opens registration: create test accounts there in the
  Keycloak console (admin login in Vault, secret `keycloak-tenant-admin-staging`
  of the project's mount) or with the staging app's own client, as below.
- Organizations are enabled in both realms. Every app client
  (`cnp-<project>-<app>`, plus `-stg` in staging) gets a service account with
  `manage-organizations`, `manage-users` and `view-users` of its own realm, and
  the `organization` scope, so the token carries the `organization` claim (the
  user's organizations; decode a real token to see its exact shape).
- Turning it off only closes registration; organizations and accounts stay.

The app manages organizations with its own client credentials, never with a
person's token:

1. `POST <issuer>/protocol/openid-connect/token` with
   `grant_type=client_credentials`, the client id above and the `client-secret`
   key of the app's secret. Cache the token until it expires.
2. With that token, call the Admin API of the realm
   (`https://auth.3istor.com/admin/realms/<realm>/...`, `<realm>` being the
   last segment of the issuer): `POST /organizations` creates an organization,
   `POST /organizations/{id}/members` adds a user (the body is the user id),
   and the organization's groups endpoint creates an org group `admins` for the
   company's own administrators. Pass `briefRepresentation=false` to member
   listings that need attributes.
3. Scope every query to the organization in the token's `organization` claim,
   never to an id sent by the client. A company admin is a member of that
   organization's group `admins`, which the app reads through the Admin API.

`manage-users` reaches every user of the realm, so a leaked client secret can
edit any account there. Keep the secret in Vault, out of logs and responses.
