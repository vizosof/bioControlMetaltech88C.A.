# ============================================================
# BioControl - Vista principal (pestañas)
# Patrón MVC: VISTA. Solo presenta información y captura eventos.
# ============================================================
import customtkinter as ctk
from views.empleados_view import EmpleadosView
from views.auditoria_view import AuditoriaView


class MainView(ctk.CTkFrame):
    """Pantalla principal con pestañas de Empleados y Bitácora."""

    def __init__(self, master, session, controller, on_logout):
        super().__init__(master, fg_color="transparent")
        self.session = session
        self.controller = controller
        self.on_logout = on_logout  # callback: vuelve al acceso

        # --- Barra superior con la sesión activa ---
        barra = ctk.CTkFrame(self, height=36)
        barra.pack(fill="x", side="top")

        ctk.CTkLabel(
            barra, text=f"Usuario: {session['username']}  |  "
                        f"Rol: {session['rol']}"
        ).pack(side="left", padx=15, pady=6)

        ctk.CTkButton(barra, text="Cerrar sesión", width=110, height=26,
                      command=on_logout).pack(side="right", padx=10)

        # --- Pestañas ---
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs.add("Empleados")
        self.tabs.add("Bitácora")

        self.empleados_view = EmpleadosView(
            self.tabs.tab("Empleados"), controller)
        self.empleados_view.pack(fill="both", expand=True)

        self.auditoria_view = AuditoriaView(
            self.tabs.tab("Bitácora"), controller)
        self.auditoria_view.pack(fill="both", expand=True)
