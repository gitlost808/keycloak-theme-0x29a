import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package", ROOT / "scripts/package.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackagingTests(unittest.TestCase):
    def test_reproducible_archive_covers_every_theme_file(self):
        metadata = json.loads((ROOT / "theme.json").read_text())
        with tempfile.TemporaryDirectory() as scratch:
            a, b = Path(scratch) / "a", Path(scratch) / "b"
            release = builder.package(ROOT / "theme/0x29a", a, "1" * 40, metadata)
            builder.package(ROOT / "theme/0x29a", b, "1" * 40, metadata)
            self.assertEqual((a / "theme.tar").read_bytes(), (b / "theme.tar").read_bytes())
            self.assertEqual((a / "theme-release.json").read_bytes(), (b / "theme-release.json").read_bytes())
            expected = {"0x29a/" + p.relative_to(ROOT / "theme/0x29a").as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (ROOT / "theme/0x29a").rglob("*") if p.is_file()}
            self.assertEqual(release["files"], expected)
            self.assertEqual(release["archive_sha256"], hashlib.sha256((a / "theme.tar").read_bytes()).hexdigest())

    def test_symlinks_cannot_become_release_assets(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root / "source"
            source.mkdir()
            (source / "leak").symlink_to("/etc/passwd")
            with self.assertRaisesRegex(ValueError, "only regular files"):
                builder.package(source, root / "output", "1" * 40, {})
