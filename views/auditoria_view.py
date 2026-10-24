# ============================================================
# BioControl - Vista de Auditoría / Bitácora
# Patrón MVC: VISTA. Solo presenta información y captura eventos.
# ============================================================
import customtkinter as ctk
from tkinter import ttk
from views.base_view import ajustar_ancho_columnas


class AuditoriaView(ctk.CTkFrame):
    """Consulta de la bitácora: quién hizo qué, cuándo y sobre qué registro."""

    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Bitácora del Sistema",
                    font=ctk.CTkFont(size=20, weight="bold")
                    ).pack(pady=(10, 5), anchor="w", padx=10)

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(fila, text="Usuario:").pack(side="left")
        self.entry_usuario = ctk.CTkEntry(fila, width=150)
        self.entry_usuario.pack(side="left", padx=(5, 15))
        self.entry_usuario.bind("<KeyRelease>", lambda e: self.refrescar())

        ctk.CTkLabel(fila, text="Entidad:").pack(side="left")
        self.entry_entidad = ctk.CTkEntry(fila, width=150)
        self.entry_entidad.pack(side="left", padx=5)
        self.entry_entidad.bind("<KeyRelease>", lambda e: self.refrescar())

        self.btn_consultar = ctk.CTkButton(
            fila, text="Consultar", width=100, command=self.refrescar)
        self.btn_consultar.pack(side="left", padx=15)

        self.columnas = ("id", "fecha_hora", "usuario_responsable", "accion",
                        "entidad", "registro_id", "detalles")
        self.tabla = ttk.Treeview(self, columns=self.columnas,
                                show="headings", height=13)
        # Barra de desplazamiento horizontal para textos largos
        self.scroll_x = ttk.Scrollbar(
            self, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(xscrollcommand=self.scroll_x.set)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.scroll_x.pack(fill="x", padx=10, pady=(0, 4))

        # Panel de detalles completos de la fila seleccionada
        self.lbl_detalle = ctk.CTkLabel(
            self, text="Seleccione una fila para ver los detalles completos.",
            anchor="w", justify="left", wraplength=980)
        self.lbl_detalle.pack(fill="x", padx=12, pady=(6, 10))
        self.tabla.bind("<<TreeviewSelect>>", self._mostrar_detalles)

        encabezados = {
            "id": "ID", "fecha_hora": "Fecha y hora",
            "usuario_responsable": "Usuario", "accion": "Acción",
            "entidad": "Entidad", "registro_id": "Reg.",
            "detalles": "Detalles",
        }
        for col in self.columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, anchor="center" if col != "detalles"
                            else "w")

        self.refrescar()

    def _mostrar_detalles(self, evento):
        """Muestra el texto completo de la entrada seleccionada."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.lbl_detalle.configure(
            text=f"{valores[2]} — {valores[3]}: {valores[6]}")

    def refrescar(self):
        usuario = self.entry_usuario.get().strip()
        entidad = self.entry_entidad.get().strip()
        try:
            registros = self.controller.bitacora(usuario, entidad)
        except Exception as e:
            registros = []
            print(f"Error al consultar bitácora: {e}")

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for reg in registros:
            self.tabla.insert("", "end", values=(
                reg["id"], reg["fecha_hora"], reg["usuario_responsable"],
                reg["accion"], reg["entidad"] or "",
                reg["registro_id"] or "", reg["detalles"]))

        # Anchos calculados con el contenido real (nada queda cortado)
        if registros:
            muestras = {col: [r[col] for r in registros]
                        for col in self.columnas}
            ajustar_ancho_columnas(self.tabla, self.columnas, muestras,
                                tope={"detalles": 480})
