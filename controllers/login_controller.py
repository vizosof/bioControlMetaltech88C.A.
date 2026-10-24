# ============================================================
# BioControl - Controlador de Acceso (login)
# Patrón MVC: CONTROLADOR. Coordina la vista de acceso y el
# modelo de usuario. No contiene SQL ni reglas de negocio.
# ============================================================
from models import usuario_model


class LoginController:
    """Conecta la vista de acceso con el modelo de usuarios."""

    def autenticar(self, username: str, password: str):
        """Devuelve el usuario autenticado o None."""
        return usuario_model.autenticar(username, password)
