# ============================================================
# BioControl - Utilidades comunes para las vistas
# ============================================================
import tkinter.font as tkfont
from tkinter import ttk


def ajustar_ancho_columnas(tabla, columnas, muestras, relleno=38,tope=None):
    """Ajusta el ancho de cada columna al contenido real.
    """
    try:
        espec = ttk.Style(tabla).lookup("Treeview", "font")
        fuente = tkfont.Font(font=espec)
    except Exception:
        fuente = tkfont.Font()
    for col in columnas:
        textos = [str(t) for t in muestras.get(col, []) if t is not None]
        if textos:
            ancho = max(fuente.measure(t) for t in textos) + relleno
        else:
            ancho = 60
        if tope and col in tope:
            ancho = min(ancho, tope[col])
        tabla.column(col, width=ancho, minwidth=ancho)
