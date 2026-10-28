import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from app.config import Settings
from app.store import DataStore


if __name__ == "__main__":
    store = DataStore(Settings())
    if not store.ready:
        raise SystemExit("La ingesta no pudo inicializar el almacenamiento")
    print(f"Ingesta G1 completada de forma idempotente: {store.source_version}")
