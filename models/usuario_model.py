# ============================================================
# BioControl - Modelo de Usuario (acceso al sistema)
# Patrón MVC: MODELO. Reglas de negocio y persistencia.
# ============================================================
import bcrypt
from config.database import get_connection


def autenticar(username: str, password: str):
    """Verifica credenciales con bcrypt. Devuelve dict del usuario o None."""
    con = get_connection()
    try:
        row = con.execute(
            """SELECT u.id, u.username, u.password_hash, r.nombre_rol
               FROM usuarios u
               JOIN roles r ON r.id = u.rol_id
               WHERE u.username = ?""",
            (username.strip(),),
        ).fetchone()

        if row is None:
            return None
        if not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
            return None

        return {
            "id": row["id"],
            "username": row["username"],
            "rol": row["nombre_rol"],
        }
    finally:
        con.close()
