# ============================================================
# BioControl - Punto de entrada de la aplicación
# UNA sola ventana raíz y UN solo bucle de eventos: las pantallas
# (acceso y principal) se intercambian dentro de la misma raíz,
# sin destruir ventanas ni anidar mainloop().
# ============================================================
import customtkinter as ctk
from config.database import init_db
from controllers.empleados_controller import EmpleadosController
from controllers.login_controller import LoginController
from views.login_view import LoginView
from views.main_view import MainView


class BioControlApp(ctk.CTk):
    """Ventana raíz de BioControl: alterna acceso y pantalla principal."""

    def __init__(self):
        super().__init__()
        self.title("BioControl - Acceso")
        self.geometry("420x420")
        self.resizable(False, False)
        self._pantalla = None
        self.usuario = None
        self.mostrar_login()

    def _limpiar(self):
        """Retira la pantalla actual sin destruir la ventana raíz."""
        if self._pantalla is not None:
            self._pantalla.destroy()
            self._pantalla = None

    def destroy(self):
        """Cancela todos los after pendientes antes de destruir la ventana."""
        try:
            for id_after in self.tk.call("after", "info"):
                self.tk.call("after", "cancel", id_after)
        except Exception:
            pass
        super().destroy()

    def mostrar_login(self):
        """Muestra la pantalla de acceso."""
        self._limpiar()
        self.usuario = None
        self.title("BioControl - Acceso")
        self.geometry("420x420")
        self.minsize(420, 420)
        self.resizable(False, False)
        self._pantalla = LoginView(self, LoginController(),self._acceso_concedido)
        self._pantalla.pack(fill="both", expand=True)

    def _acceso_concedido(self, usuario: dict):
        """Muestra la pantalla principal con el usuario autenticado."""
        self._limpiar()
        self.usuario = usuario
        self.title(f"BioControl - {usuario['rol']}: {usuario['username']}")
        self.geometry("1080x600")
        self.minsize(960, 540)
        self.resizable(True, True)
        controller = EmpleadosController(usuario)
        self._pantalla = MainView(self, usuario, controller,self.mostrar_login)
        self._pantalla.pack(fill="both", expand=True)


if __name__ == "__main__":
    init_db()  # crea estructura y datos de prueba si la base está vacía
    app = BioControlApp()
    app.mainloop()
