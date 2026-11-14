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

Use the exact image in `theme.json` for a local preview:

```sh
docker run --rm -p 127.0.0.1:18080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -v "$PWD/theme/0x29a:/opt/keycloak/themes/0x29a:ro" \
  <tested_keycloak_image from theme.json> start-dev
```

Create a throwaway realm at http://127.0.0.1:18080/admin/ and select `0x29a`
for its login and account themes. Development mode disables theme caching.
Check login, password reset, narrow screens, reduced motion, and the Account
Console when changing CSS or upgrading Keycloak; this theme styles upstream
markup and PatternFly selectors. `theme.json` records the exact image against
which compatibility was reviewed.

## Release contract

Commit first, then run `make package OUTPUT=/absolute/empty/staging`. A release
is `theme.tar.gz` plus `theme-release.json`, recording the full source commit,
exact tested Keycloak image, archive SHA-256, and SHA-256 of every file. The
archive contains only regular files under `0x29a/`; timestamps, owners, modes,
and gzip headers are fixed so repeated builds produce identical bytes.

The infra repository vendors this release dependency and pins its manifest.
Its release helper imports the two files from a pristine source checkout;
CI rebuilds the exact source commit and compares the bytes. Deployment verifies
the manifest, archive members, file hashes, and Keycloak compatibility before
installing static data. No source scripts execute on the managed host, and no
publisher account, new service, or runtime network fetch is required.

Production realm settings, secrets, Compose configuration, and version
selection remain in infra. Pushing here does not deploy the theme. Theme
changes recreate Keycloak through infra's configuration hash to clear its
production cache; hashed asset URLs separately handle browser caches.

## Provenance

History before the extraction commit comes from `apps/keycloak/themes/0x29a`
in `gitlost808/infra` using `git subtree split`. The source assets are unchanged
by extraction. The Kode Mono font's SIL Open Font License is retained at
`theme/0x29a/OFL.txt`.
