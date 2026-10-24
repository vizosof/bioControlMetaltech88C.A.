# ============================================================
# BioControl - Vista de Acceso (login)
# Patrón MVC: VISTA. Solo presenta información y captura eventos.
# ============================================================
import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    """Pantalla de inicio de sesión, mostrada dentro de la ventana raíz."""

    def __init__(self, master, controller, on_login_ok):
        super().__init__(master, fg_color="transparent")
        self.controller = controller    # LoginController
        self.on_login_ok = on_login_ok  # callback: notifica el acceso

        ctk.CTkLabel(self, text="BioControl",
                     font=ctk.CTkFont(size=28, weight="bold")
                     ).pack(pady=(50, 5))
        ctk.CTkLabel(self, text="Control de asistencia Metaltech 88",
                     text_color="#7F8C8D").pack(pady=(0, 30))

        ctk.CTkLabel(self, text="Usuario").pack()
        self.entry_usuario = ctk.CTkEntry(self, width=240)
        self.entry_usuario.pack(pady=(0, 10))

        ctk.CTkLabel(self, text="Contraseña").pack()
        self.entry_password = ctk.CTkEntry(self, width=240, show="*")
        self.entry_password.pack(pady=(0, 15))
        self.entry_password.bind("<Return>", lambda e: self.validar())

        self.btn_ingresar = ctk.CTkButton(self, text="Ingresar", width=240,
                                          command=self.validar)
        self.btn_ingresar.pack()

        self.lbl_error = ctk.CTkLabel(self, text="", text_color="#B03A2E",
                                      wraplength=300)
        self.lbl_error.pack(pady=(10, 0))

    def validar(self):
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            self.lbl_error.configure(text="Ingrese usuario y contraseña.")
            return

        usuario = self.controller.autenticar(username, password)
        if usuario is None:
            self.lbl_error.configure(
                text="Usuario o contraseña incorrectos.")
            return

        self.on_login_ok(usuario)
