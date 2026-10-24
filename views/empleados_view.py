# ============================================================
# BioControl - Vista de Empleados (CRUD en pantalla)
# Patrón MVC: VISTA. Solo presenta información y captura eventos.
# No contiene SQL ni reglas de negocio.
# ============================================================
import customtkinter as ctk
from tkinter import ttk
from views.base_view import ajustar_ancho_columnas

# Etiquetas visibles con tildes para cada campo del formulario
ETIQUETAS = {"cedula": "Cédula", "nombre": "Nombre", "cargo": "Cargo",
             "foto_path": "Ruta de foto"}


class EmpleadosView(ctk.CTkFrame):
    """Pantalla de gestión de empleados: buscar, crear, editar,
    activar/desactivar y eliminar."""

    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._build()

    def _build(self):
        # --- Barra superior: título, búsqueda y acciones ---
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(barra, text="Gestión de Empleados",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        self.btn_nuevo = ctk.CTkButton(
            barra, text="+ Nuevo", width=90, command=self.abrir_formulario)
        self.btn_nuevo.pack(side="right", padx=(5, 0))

        self.btn_editar = ctk.CTkButton(
            barra, text="Editar", width=90, command=self.editar_seleccionado)
        self.btn_editar.pack(side="right", padx=5)

        # --- Fila de búsqueda ---
        fila_bus = ctk.CTkFrame(self, fg_color="transparent")
        fila_bus.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(fila_bus, text="Buscar:").pack(side="left")
        self.entry_buscar = ctk.CTkEntry(fila_bus, width=300)
        self.entry_buscar.pack(side="left", padx=8)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.refrescar())

        self.btn_eliminar = ctk.CTkButton(
            fila_bus, text="Eliminar", width=90, fg_color="#B03A2E",
            hover_color="#7B241C", command=self.eliminar_seleccionado)
        self.btn_eliminar.pack(side="right")

        self.btn_estado = ctk.CTkButton(
            fila_bus, text="Activar/Desactivar", width=140,
            command=self.cambiar_estado)
        self.btn_estado.pack(side="right", padx=5)

        # --- Tabla de empleados ---
        self.columnas = ("id", "cedula", "nombre", "cargo", "estado")
        self.tabla = ttk.Treeview(self, columns=self.columnas,
                                  show="headings", height=15)
        self.scroll_x = ttk.Scrollbar(
            self, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(xscrollcommand=self.scroll_x.set)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.scroll_x.pack(fill="x", padx=10, pady=(0, 10))
        self.tabla.bind("<Double-1>", lambda e: self.editar_seleccionado())

        # --- Barra de estado ---
        self.lbl_mensaje = ctk.CTkLabel(self, text="", text_color="#2E86C1")
        self.lbl_mensaje.pack(pady=(0, 10))

        self.refrescar()

    # ---- Operaciones de la vista ----
    def refrescar(self):
        texto = self.entry_buscar.get().strip()
        try:
            empleados = self.controller.listar(texto)
        except Exception as e:
            self._mensaje(f"Error al consultar: {e}", ok=False)
            return

        # Anchos calculados con el contenido real (nada queda cortado)
        encabezados = {"id": "ID", "cedula": "Cédula", "nombre": "Nombre",
                       "cargo": "Cargo", "estado": "Estado"}
        for col in self.columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, anchor="center")
        muestras = {col: [encabezados[col]] +
                    [emp[col] for emp in empleados] for col in self.columnas}
        ajustar_ancho_columnas(self.tabla, self.columnas, muestras)

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for emp in empleados:
            self.tabla.insert("", "end", values=(
                emp["id"], emp["cedula"], emp["nombre"],
                emp["cargo"], emp["estado"]))

    def _seleccion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self._mensaje("Seleccione un empleado de la tabla.", ok=False)
            return None
        valores = self.tabla.item(seleccion[0], "values")
        return int(valores[0])

    def abrir_formulario(self, empleado_id=None):
        FormularioEmpleado(self, self.controller, empleado_id)

    def editar_seleccionado(self):
        empleado_id = self._seleccion()
        if empleado_id:
            self.abrir_formulario(empleado_id)

    def cambiar_estado(self):
        empleado_id = self._seleccion()
        if empleado_id:
            ok, msg = self.controller.cambiar_estado(empleado_id)
            self._mensaje(msg, ok)
            self.refrescar()

    def eliminar_seleccionado(self):
        empleado_id = self._seleccion()
        if empleado_id:
            ok, msg = self.controller.eliminar(empleado_id)
            self._mensaje(msg, ok)
            self.refrescar()

    def _mensaje(self, texto, ok=True):
        self.lbl_mensaje.configure(
            text=texto, text_color="#1E8449" if ok else "#B03A2E")


class FormularioEmpleado(ctk.CTkToplevel):
    """Ventana de creación/edición de un empleado."""

    def __init__(self, vista, controller, empleado_id=None):
        super().__init__(vista)
        self.vista = vista
        self.controller = controller
        self.empleado_id = empleado_id

        if empleado_id:
            self.title("Editar Empleado")
            datos = controller.obtener(empleado_id)
        else:
            self.title("Nuevo Empleado")
            datos = {"cedula": "", "nombre": "", "cargo": "", "foto_path": ""}

        # Tamaño por contenido: el formulario no debe quedar cortado
        self.resizable(False, False)
        self.grab_set()  # ventana modal

        ctk.CTkLabel(self, text=("Editar" if empleado_id else "Nuevo") +
                    " Empleado", font=ctk.CTkFont(size=16, weight="bold")
                    ).pack(pady=(15, 10))

        self.campos = {}
        for campo in ("cedula", "nombre", "cargo", "foto_path"):
            etiqueta = ETIQUETAS[campo] + (
                " (opcional)" if campo == "foto_path" else " *")
            ctk.CTkLabel(self, text=etiqueta).pack(anchor="w", padx=20)
            entrada = ctk.CTkEntry(self, width=330)
            entrada.insert(0, datos.get(campo) or "")
            entrada.pack(padx=20, pady=(0, 8))
            self.campos[campo] = entrada

        self.lbl_error = ctk.CTkLabel(self, text="", text_color="#B03A2E",
                                      wraplength=330)
        self.lbl_error.pack(padx=20)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar", width=120,
                                         command=self.guardar)
        self.btn_guardar.pack(pady=(5, 15))

        # Centrar la ventana sobre la vista de empleados
        self.update_idletasks()
        x = self.vista.winfo_rootx() + (
            (self.vista.winfo_width() - self.winfo_width()) // 2)
        y = self.vista.winfo_rooty() + 60
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def guardar(self):
        datos = {campo: entrada.get() for campo, entrada
                 in self.campos.items()}
        if self.empleado_id:
            ok, msg = self.controller.actualizar(self.empleado_id, datos)
        else:
            ok, msg = self.controller.crear(datos)

        if ok:
            self.destroy()
            self.vista.refrescar()
            self.vista._mensaje(msg, True)
        else:
            self.lbl_error.configure(text=msg)
