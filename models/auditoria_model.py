# ============================================================
# BioControl - Modelo de Auditoría / Bitácora
# Patrón MVC: MODELO. Reglas de negocio y persistencia.
# ============================================================
from config.database import get_connection

ACCIONES = ("CREACION", "ACTUALIZACION", "ELIMINACION", "DESACTIVACION",
            "ACTIVACION", "LOGIN", "CONSULTA", "CORRECCION")


def registrar(con, usuario: str, accion: str, entidad: str,
              registro_id, detalles: str) -> None:
    """Escribe una entrada en la bitácora DENTRO de la transacción actual.

    Recibe la conexión abierta para que el cambio de negocio y su
    auditoría se guarden en la misma transacción (o se reviertan juntos).
    """
    con.execute(
        """INSERT INTO auditoria
           (usuario_responsable, accion, entidad, registro_id, detalles)
           VALUES (?, ?, ?, ?, ?)""",
        (usuario, accion, entidad, registro_id, detalles),
    )


def listar(usuario: str = "", entidad: str = "", limite: int = 200):
    """Consulta la bitácora con filtros opcionales, más reciente primero."""
    con = get_connection()
    try:
        query = "SELECT * FROM auditoria WHERE 1=1"
        params = []
        if usuario:
            query += " AND usuario_responsable LIKE ?"
            params.append(f"%{usuario}%")
        if entidad:
            query += " AND entidad LIKE ?"
            params.append(f"%{entidad}%")
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limite)
        rows = con.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()
