# ============================================================
# BioControl - Controlador de Empleados
# Patrón MVC: CONTROLADOR. Coordina vistas y modelos.
# No contiene SQL ni reglas de negocio.
# ============================================================
from models import empleado_model
from models import auditoria_model
from models.empleado_model import ValidationError


class EmpleadosController:
    """Conecta la vista de empleados con el modelo."""

    def __init__(self, session: dict):
        self.session = session  # usuario autenticado {"username", "rol", ...}

    # ---- Consultas ----
    def listar(self, texto=""):
        return empleado_model.buscar(texto)

    def obtener(self, empleado_id):
        return empleado_model.obtener(empleado_id)

    # ---- Operaciones CRUD ----
    def crear(self, datos: dict):
        try:
            nuevo_id = empleado_model.crear(datos, self.session["username"])
            return True, f"Empleado registrado con ID {nuevo_id}."
        except ValidationError as e:
            return False, str(e)

    def actualizar(self, empleado_id: int, datos: dict):
        try:
            empleado_model.actualizar(empleado_id, datos,
                                      self.session["username"])
            return True, "Empleado actualizado."
        except ValidationError as e:
            return False, str(e)

    def cambiar_estado(self, empleado_id: int):
        try:
            estado = empleado_model.cambiar_estado(
                empleado_id, self.session["username"])
            return True, f"Nuevo estado: {estado}."
        except ValidationError as e:
            return False, str(e)

    def eliminar(self, empleado_id: int):
        try:
            empleado_model.eliminar(empleado_id, self.session["username"])
            return True, "Empleado eliminado."
        except ValidationError as e:
            return False, str(e)

    # ---- Bitácora ----
    def bitacora(self, usuario="", entidad=""):
        return auditoria_model.listar(usuario, entidad)
