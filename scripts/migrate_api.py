import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from app.config import Settings
from app.migrations import apply_migrations


if __name__ == "__main__":
    applied = apply_migrations(Settings())
    print(f"Migraciones aplicadas: {', '.join(applied) if applied else 'ninguna'}")
