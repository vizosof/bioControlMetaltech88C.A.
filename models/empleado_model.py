# ============================================================
# BioControl - Modelo de Empleados (CRUD + reglas de negocio)
# Patrón MVC: MODELO. Validaciones, reglas y persistencia.
# Cada operación y su bitácora se guardan en la MISMA transacción.
# ============================================================
import re
import sqlite3
from config.database import get_connection
from models import auditoria_model

PATRON_CEDULA = re.compile(r"V-[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}")


class ValidationError(Exception):
    """Error de regla de negocio, mostrable al usuario."""


def _validar(cedula: str, nombre: str, cargo: str) -> None:
    """Aplica las reglas de negocio del formulario de empleados."""
    if not cedula or not cedula.strip():
        raise ValidationError("La cédula es obligatoria.")
    if not PATRON_CEDULA.match(cedula.strip()):
        raise ValidationError("La cédula debe tener el formato V-00.000.000.")
    if not nombre or not nombre.strip():
        raise ValidationError("El nombre es obligatorio.")
    if len(nombre.strip()) < 3:
        raise ValidationError("El nombre debe tener al menos 3 caracteres.")
    if not cargo or not cargo.strip():
        raise ValidationError("El cargo es obligatorio.")


def buscar(texto: str = ""):
    """Lista empleados; si hay texto, filtra por nombre, cédula o cargo."""
    con = get_connection()
    try:
        query = "SELECT * FROM empleados"
        params = []
        if texto and texto.strip():
            filtro = f"%{texto.strip()}%"
            query += (" WHERE nombre LIKE ? OR cedula LIKE ? OR cargo LIKE ?")
            params = [filtro, filtro, filtro]
        query += " ORDER BY nombre"
        rows = con.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def obtener(empleado_id: int):
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM empleados WHERE id = ?", (empleado_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def crear(datos: dict, usuario: str) -> int:
    """Registra un empleado. Valida reglas y cédula duplicada."""
    _validar(datos.get("cedula", ""), datos.get("nombre", ""),
            datos.get("cargo", ""))

    con = get_connection()
    try:
        con.execute("BEGIN")
        duplicado = con.execute(
            "SELECT id FROM empleados WHERE cedula = ?",
            (datos["cedula"].strip(),),
        ).fetchone()
        if duplicado:
            raise ValidationError(
                f"Ya existe un empleado con la cédula {datos['cedula']}."
            )

        cur = con.execute(
            """INSERT INTO empleados (cedula, nombre, cargo, foto_path, estado)
            VALUES (?, ?, ?, ?, 'Activo')""",
            (datos["cedula"].strip(), datos["nombre"].strip(),
            datos["cargo"].strip(), datos.get("foto_path") or None),
        )
        nuevo_id = cur.lastrowid
        auditoria_model.registrar(
            con, usuario, "CREACION", "EMPLEADOS", nuevo_id,
            f"Alta de {datos['nombre'].strip()} "
            f"({datos['cedula'].strip()})."
        )
        con.commit()
        return nuevo_id # type: ignore
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def actualizar(empleado_id: int, datos: dict, usuario: str) -> None:
    """Edita un empleado, registrando en bitácora qué campos cambiaron."""
    _validar(datos.get("cedula", ""), datos.get("nombre", ""),
            datos.get("cargo", ""))

    con = get_connection()
    try:
        con.execute("BEGIN")
        actual = con.execute(
            "SELECT * FROM empleados WHERE id = ?", (empleado_id,)
        ).fetchone()
        if actual is None:
            raise ValidationError("El empleado no existe.")

        duplicado = con.execute(
            "SELECT id FROM empleados WHERE cedula = ? AND id != ?",
            (datos["cedula"].strip(), empleado_id),
        ).fetchone()
        if duplicado:
            raise ValidationError(
                f"La cédula {datos['cedula']} pertenece a otro empleado."
            )

        cambios = []
        for campo in ("cedula", "nombre", "cargo", "foto_path"):
            nuevo = (datos.get(campo) or "").strip() if campo != "foto_path" else (datos.get(campo) or "")
            viejo = actual[campo] or ""
            if nuevo != viejo:
                cambios.append(f"{campo}: '{viejo}' -> '{nuevo}'")

        if not cambios:
            con.rollback()
            return  # No hubo cambios: no se escribe bitácora

        con.execute(
            """UPDATE empleados
            SET cedula = ?, nombre = ?, cargo = ?, foto_path = ?
            WHERE id = ?""",
            (datos["cedula"].strip(), datos["nombre"].strip(),
            datos["cargo"].strip(), datos.get("foto_path") or None,
            empleado_id),
        )
        auditoria_model.registrar(
            con, usuario, "ACTUALIZACION", "EMPLEADOS", empleado_id,
            "Cambios: " + "; ".join(cambios)
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def cambiar_estado(empleado_id: int, usuario: str) -> str:
    """Alterna entre Activo e Inactivo (nunca borra el historial)."""
    con = get_connection()
    try:
        con.execute("BEGIN")
        actual = con.execute(
            "SELECT * FROM empleados WHERE id = ?", (empleado_id,)
        ).fetchone()
        if actual is None:
            raise ValidationError("El empleado no existe.")

        nuevo_estado = "Inactivo" if actual["estado"] == "Activo" else "Activo"
        con.execute(
            "UPDATE empleados SET estado = ? WHERE id = ?",
            (nuevo_estado, empleado_id),
        )
        accion = "DESACTIVACION" if nuevo_estado == "Inactivo" else "ACTIVACION"
        auditoria_model.registrar(
            con, usuario, accion, "EMPLEADOS", empleado_id,
            f"{actual['nombre']} pasó a estado {nuevo_estado}."
        )
        con.commit()
        return nuevo_estado
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def eliminar(empleado_id: int, usuario: str) -> None:
    """Elimina un empleado sin historial de asistencia.

    Regla de negocio: si el empleado tiene marcajes, la base de datos
    lo impide (ON DELETE RESTRICT) y se informa al usuario.
    """
    con = get_connection()
    try:
        con.execute("BEGIN")
        actual = con.execute(
            "SELECT * FROM empleados WHERE id = ?", (empleado_id,)
        ).fetchone()
        if actual is None:
            raise ValidationError("El empleado no existe.")

        try:
            con.execute("DELETE FROM empleados WHERE id = ?", (empleado_id,))
        except sqlite3.IntegrityError:
            raise ValidationError(
                "No se puede eliminar: el empleado tiene marcajes "
                "registrados. Desactívelo para conservar su historial."
            )

        auditoria_model.registrar(
            con, usuario, "ELIMINACION", "EMPLEADOS", empleado_id,
            f"Baja de {actual['nombre']} ({actual['cedula']})."
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
