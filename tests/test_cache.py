"""The 0x29a Keycloak theme's cache versions.

Keycloak serves theme files with a 30-day max-age under /resources/<version>/,
whose version changes only with Keycloak itself. Each of the theme's own files
is therefore referenced with ?v= and the start of its SHA-256, so a changed
file gets a new URL that browsers fetch instead of their cached copy.
"""

import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme/0x29a"
THEME_TYPES = ("login", "account")
URL = re.compile(r'url\("([^")]+)"\)')


def version(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10]


def references(theme_type):
    """Each theme file reference as (where, path, ?v= value or None, target)."""
    resources = THEME / theme_type / "resources"
    properties = (THEME / theme_type / "theme.properties").read_text()
    for line in properties.splitlines():
        key, _, value = line.partition("=")
        if key.strip() in ("styles", "scripts"):
            for entry in value.split():
                path, _, query = entry.partition("?")
                yield "theme.properties", entry, query.removeprefix("v=") or None, resources / path
    for stylesheet in resources.rglob("*.css"):
        for entry in URL.findall(stylesheet.read_text()):
            path, _, query = entry.partition("?")
            yield stylesheet.name, entry, query.removeprefix("v=") or None, stylesheet.parent / path


class KeycloakThemeCacheTests(unittest.TestCase):
    def test_own_files_carry_their_content_version(self):
        checked = 0
        for theme_type in THEME_TYPES:
            for source, entry, declared, target in references(theme_type):
                # css/styles.css belongs to the parent theme, not this one.
                if not target.resolve().is_file():
                    continue
                checked += 1
                with self.subTest(theme=theme_type, source=source, entry=entry):
                    expected = version(target.resolve())
                    self.assertEqual(declared, expected,
                                     f"reference it as ?v={expected} so browsers fetch the new file")
        self.assertGreaterEqual(checked, 6)


if __name__ == "__main__":
    unittest.main()
