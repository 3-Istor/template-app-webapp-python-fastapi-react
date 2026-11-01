# Reading the logged-in user in the backend

The gateway's OIDC filter logs the user in. When the app's exposure is
`project members` or `project admins` (non-empty `ingress.allowedGroups` in
`deploy/values-frontend.yaml`), the gateway also checks the token and forwards
it to nginx as `Authorization: Bearer <JWT>`. nginx passes it on to `/api/*`.
In any other exposure, no identity reaches the backend.

Verify the token in the backend anyway. Every pod of the project, and a few
platform namespaces, can reach the backend Service without going through the
gateway, so a header on its own proves nothing. The issuer is `https://auth.3istor.com/realms/<project>`, where
`<project>` is `project_name` in `deploy/values-backend.yaml`. A project with
its own Keycloak uses `https://auth-<project>.3istor.com/realms/<realm>`.

1. Pin `PyJWT[crypto]` in `backend/requirements.txt`.
2. Add `oidc_issuer: str = ""` to `Settings`, and set `OIDC_ISSUER` under `env:`
   in `deploy/values-backend.yaml`.
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
(`project-members`, `project-admins`). Group names come without a leading
slash, as `ingress.allowedGroups` expects them.
