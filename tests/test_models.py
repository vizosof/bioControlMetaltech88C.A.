# ============================================================
# BioControl - Pruebas de lógica de negocio (sin interfaz)
# Ejecutar:  python tests/test_models.py
# ============================================================
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config.database  # noqa: E402
from config.database import init_db  # noqa: E402
from models import usuario_model, empleado_model, auditoria_model  # noqa: E402
from models.empleado_model import ValidationError  # noqa: E402

EXITOSOS = 0
FALLIDOS = 0

# Las pruebas SIEMPRE usan una base temporal: nunca tocan la base
# de trabajo biocontrol.db del usuario.
_DIR_TEMPORAL = tempfile.TemporaryDirectory()
config.database.DB_PATH = Path(_DIR_TEMPORAL.name) / "biocontrol_pruebas.db"
DB_PATH = config.database.DB_PATH


def prueba(nombre, condicion):
    global EXITOSOS, FALLIDOS
    if condicion:
        EXITOSOS += 1
        print(f"  [OK]    {nombre}")
    else:
        FALLIDOS += 1
        print(f"  [FALLO] {nombre}")


def main():
    # Base temporal aislada para la prueba
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()

    print("1. Autenticación")
    usuario = usuario_model.autenticar("admin", "biocontrol2026")
    prueba("Login admin/biocontrol2026 correcto", usuario is not None)
    prueba("Login con contraseña incorrecto",
          usuario_model.autenticar("admin", "malaclave") is None)
    prueba("Login con usuario inexistente",
          usuario_model.autenticar("noexiste", "biocontrol2026") is None)

    print("2. Crear empleado")
    nuevo_id = empleado_model.crear(
        {"cedula": "V-99.888.777", "nombre": "Empleado de Prueba",
         "cargo": "Tester"}, "admin")
    prueba("Empleado creado", nuevo_id > 0)
    try:
        empleado_model.crear(
            {"cedula": "V-99.888.777", "nombre": "Duplicado",
             "cargo": "X"}, "admin")
        prueba("Cédula duplicada rechazada", False)
    except ValidationError:
        prueba("Cédula duplicada rechazada", True)
    try:
        empleado_model.crear(
            {"cedula": "123", "nombre": "Mal formato", "cargo": "X"}, "admin")
        prueba("Formato de cédula inválido rechazado", False)
    except ValidationError:
        prueba("Formato de cédula inválido rechazado", True)

    print("3. Buscar y consultar")
    resultados = empleado_model.buscar("Prueba")
    prueba("Búsqueda por texto encuentra al empleado",
          any(e["id"] == nuevo_id for e in resultados))
    prueba("Consulta individual correcta",
          empleado_model.obtener(nuevo_id)["nombre"] == "Empleado de Prueba")

    print("4. Actualizar empleado")
    empleado_model.actualizar(
        nuevo_id, {"cedula": "V-99.888.777",
                   "nombre": "Empleado Editado", "cargo": "Tester Sr"},
        "admin")
    prueba("Edición aplicada",
          empleado_model.obtener(nuevo_id)["nombre"] == "Empleado Editado")

    print("5. Bitácora")
    registros = auditoria_model.listar()
    ultimas = [r for r in registros if r["entidad"] == "EMPLEADOS"
               and r["registro_id"] == nuevo_id]
    acciones = [r["accion"] for r in ultimas]
    prueba("Bitácora registró CREACION", "CREACION" in acciones)
    prueba("Bitácora registró ACTUALIZACION", "ACTUALIZACION" in acciones)
    prueba("Bitácora asocia el usuario responsable",
          all(r["usuario_responsable"] == "admin" for r in ultimas))

    print("6. Desactivar / activar")
    estado = empleado_model.cambiar_estado(nuevo_id, "admin")
    prueba("Desactivado", estado == "Inactivo")
    estado = empleado_model.cambiar_estado(nuevo_id, "admin")
    prueba("Reactivado", estado == "Activo")

    print("7. Reglas de borrado")
    empleado_model.eliminar(nuevo_id, "admin")
    prueba("Empleado sin marcajes se puede eliminar",
          empleado_model.obtener(nuevo_id) is None)
    try:
        empleado_model.eliminar(1, "admin")  # empleado 1 tiene marcajes
        prueba("Empleado con marcajes NO se puede eliminar", False)
    except ValidationError:
        prueba("Empleado con marcajes NO se puede eliminar", True)

    print("8. Persistencia (reabrir conexión)")
    con_total = auditoria_model.listar()
    prueba("Bitácora conserva la eliminación",
          any(r["accion"] == "ELIMINACION" and
              r["registro_id"] == nuevo_id for r in con_total))
    prueba("Empleado 1 sigue activo",
          empleado_model.obtener(1)["estado"] == "Activo")

    print()
    print(f"RESULTADO: {EXITOSOS} exitosas, {FALLIDOS} fallidas")
    sys.exit(1 if FALLIDOS else 0)


if __name__ == "__main__":
    main()
