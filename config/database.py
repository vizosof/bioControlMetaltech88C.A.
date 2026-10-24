# ============================================================
# BioControl - Capa de configuración de base de datos
# Patrón MVC: este módulo NO pertenece al modelo; solo abre
# conexiones y prepara la base de datos inicial.
# ============================================================
import sqlite3
from pathlib import Path

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "biocontrol.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SEED_PATH = BASE_DIR / "database" / "seed.sql"


def get_connection() -> sqlite3.Connection:
    """Abre una conexión con integridad referencial activada."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db() -> None:
    """Crea la estructura y carga los datos de prueba si la base está vacía.

    Importante: CREATE TABLE IF NOT EXISTS no modifica tablas existentes.
    Para aplicar cambios de esquema hay que usar una base nueva.
    """
    con = get_connection()
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.commit()

        usuarios = con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        if usuarios == 0:
            con.executescript(SEED_PATH.read_text(encoding="utf-8"))
            con.commit()
    finally:
        con.close()
