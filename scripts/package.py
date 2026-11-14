#!/usr/bin/env python3
"""Produce a deterministic static theme archive and its release manifest."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "gitlost808/keycloak-theme-0x29a"


def package(source, output, revision, metadata):
    """Package regular files only with fixed, reproducible GNU tar metadata."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("A complete source commit SHA is required")
    paths = sorted(source.rglob("*"))
    if any(path.is_symlink() or not (path.is_file() or path.is_dir()) for path in paths):
        raise ValueError("Themes may contain only regular files and directories")
    files = {}
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for path in paths:
            if not path.is_file():
                continue
            name = "0x29a/" + path.relative_to(source).as_posix()
            data = path.read_bytes()
            files[name] = hashlib.sha256(data).hexdigest()
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            entry.mode = 0o644
            entry.uid = entry.gid = entry.mtime = 0
            archive.addfile(entry, io.BytesIO(data))
    # Plain GNU tar has no platform/library-sensitive compression layer.
    # Git compresses the vendored dependency in the consuming repository.
    artifact = tar_bytes.getvalue()
    manifest = {**metadata, "source_repository": REPOSITORY, "source_revision": revision,
                "archive_sha256": hashlib.sha256(artifact).hexdigest(), "files": files}
    output.mkdir(parents=True, exist_ok=True)
    (output / "theme.tar").write_bytes(artifact)
    (output / "theme-release.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="empty staging directory outside this repository")
    output = parser.parse_args().output.resolve()
    if output.is_relative_to(ROOT) or (output.exists() and any(output.iterdir())):
        raise SystemExit("Use an empty staging directory outside the source checkout")
    git = ["git", "-C", str(ROOT)]
    if subprocess.check_output(git + ["status", "--porcelain", "--untracked-files=all"], text=True).strip():
        raise SystemExit("Commit the theme first; releases require a pristine source checkout")
    revision = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    manifest = package(ROOT / "theme/0x29a", output, revision, json.loads((ROOT / "theme.json").read_text()))
    print(f"Packaged {manifest['theme']} from {revision}: sha256:{manifest['archive_sha256']}")


if __name__ == "__main__":
    main()
