

from pathlib import Path


def assets_cwd() -> Path:
    return Path(__file__).parent / 'assets'