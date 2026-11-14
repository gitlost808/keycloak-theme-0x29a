# 0x29a Keycloak theme

The login and Account Console theme for the 0x29a realm: Kode Mono,
`#859900` on `#060606`, outlined panels, and typed login headings.

`theme/0x29a/login` extends Keycloak's `keycloak.v2`; it keeps upstream templates
and messages except for the home-link footer. `account` extends `keycloak.v3`
and recolours PatternFly. The account script selects PatternFly's dark theme.
Reduced-motion preferences are respected by the login animation.

## Develop and preview

Run `make test`. There are no package dependencies. Theme cache-version tests
report the SHA-256 prefix required in each stylesheet/script/font URL after
an edit. Keep both stylesheets' shared font and colour tokens coordinated with
the dummypage site's `src/common/styles`.

Build the image with `make test-image`, then preview it locally:

```sh
docker run --rm -p 127.0.0.1:18080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  keycloak-theme-0x29a:local start-dev
```

Create a throwaway realm at http://127.0.0.1:18080/admin/ and select `0x29a`
for its login and account themes. Development mode disables theme caching.
Check login, password reset, narrow screens, reduced motion, and the Account
Console when changing CSS or upgrading Keycloak; this theme styles upstream
markup and PatternFly selectors. The Dockerfile pins the exact upstream image
against which compatibility is reviewed. For live editing, add
`-v "$PWD/theme/0x29a:/opt/keycloak/themes/0x29a:ro"` before the image name.

## Build and release

The Dockerfile extends an immutable upstream Keycloak image and copies this
repository's theme into `/opt/keycloak/themes/0x29a`. It preserves the upstream
entrypoint, user, server behavior, and configuration contract. It adds no
runtime installer or theme bind mount.

`make test-image` builds the image, compares every installed theme file with
its source, and runs the Keycloak version command. CI runs these checks on
pushes and pull requests. Successful pushes publish a candidate image at
`ghcr.io/gitlost808/keycloak-theme-0x29a:sha-<full-commit>`; pull requests only
build and verify. Images are linked to this source repository through OCI
source/revision labels. The package must be public for unauthenticated host
pulls.

Infra selects a reviewed image by immutable digest in its Compose definition.
A source push never changes the production image pin. An image bump recreates
Keycloak and clears its server-side theme cache; content-versioned asset URLs
handle browser caches. Keycloak upgrades start by updating the upstream image
pin here and checking login and Account Console compatibility.

Production realm settings, secrets, runtime flags, database volumes, and
routing stay in infra. No theme archive is committed there.

## Provenance

History before the extraction commit comes from `apps/keycloak/themes/0x29a`
in `gitlost808/infra` using `git subtree split`. The source assets are unchanged
by extraction. The Kode Mono font's SIL Open Font License is retained at
`theme/0x29a/OFL.txt`.
