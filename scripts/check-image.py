#!/usr/bin/env python3
"""Verify the built image contains exactly the repository's theme files."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def tree(directory):
    result = {}
    for path in directory.rglob("*"):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError(f"Unexpected theme entry: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    image = parser.parse_args().image
    container = subprocess.check_output(["docker", "create", image, "--version"], text=True).strip()
    try:
        with tempfile.TemporaryDirectory(prefix="keycloak-theme-image-") as scratch:
            target = Path(scratch) / "theme"
            subprocess.run(["docker", "cp", f"{container}:/opt/keycloak/themes/0x29a", str(target)], check=True)
            if tree(ROOT / "theme/0x29a") != tree(target):
                raise SystemExit("The image theme does not match the source tree")
    finally:
        subprocess.run(["docker", "rm", container], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["docker", "run", "--rm", image, "--version"], check=True)
    print("Image theme matches every source file; Keycloak entrypoint works.")


if __name__ == "__main__":
    main()
