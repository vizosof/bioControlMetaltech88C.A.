# BioControl - Fase 1 (Actividad Sumativa 2)

Aplicación de escritorio en Python con patrón **MVC** (Modelo-Vista-Controlador)
para la gestión de empleados del sistema de control de asistencia de
Metaltech 88. Base de datos **SQLite**, interfaz **CustomTkinter** y bitácora
de auditoría integrada.

## Arquitectura

La aplicación usa **una sola ventana raíz y un solo bucle de eventos**:
la pantalla de acceso y la pantalla principal se intercambian dentro de la
misma raíz (`main.BioControlApp`).

## Estructura del proyecto (MVC)

```text
BioControl/
├── main.py                    # Raíz única: alterna acceso y pantalla principal
├── requirements.txt           # Dependencias
├── config/
│   └── database.py            # Conexiones SQLite e inicialización de la base
├── models/                   # MODELO: reglas de negocio y persistencia
│   ├── usuario_model.py      #   Autenticación con bcrypt
│   ├── empleado_model.py     #   CRUD de empleados + validaciones
│   └── auditoria_model.py    #   Bitácora del sistema
├── views/                    # VISTA: pantallas (sin SQL ni reglas)
│   ├── base_view.py          #   Utilidades comunes (anchos de columnas)
│   ├── login_view.py         #   Acceso
│   ├── main_view.py          #   Pantalla principal con pestañas
│   ├── empleados_view.py     #   Gestión de empleados (CRUD)
│   └── auditoria_view.py     #   Consulta de bitácora
├── controllers/              # CONTROLADOR: coordina vistas y modelos
│   ├── login_controller.py   #   Autenticación
│   └── empleados_controller.py
└── database/
    ├── schema.sql            # Estructura de la base de datos
    └── seed.sql              # Datos de prueba (5 por tabla clave)
    
```

## Cómo ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación
python main.py
```

La primera ejecución crea `biocontrol.db` con el esquema y los datos de
prueba de forma automática (solo si la base está vacía).

## Credenciales de demostración

| Usuario | Contraseña | Rol |
|---|---|---|
| admin | biocontrol2026 | Administrador |
| gerencia | biocontrol2026 | Gerente |
| supervisor | biocontrol2026 | Administrador |
| consulta | biocontrol2026 | Gerente |
| auditor | biocontrol2026 | Administrador |

## Reglas de negocio implementadas

- Cédula obligatoria con formato `V-00.000.000` y única en el sistema.
- Nombre y cargo obligatorios (nombre mínimo de 3 caracteres).
- Un empleado con marcajes registrados **no se puede eliminar**: se desactiva
  para conservar su historial de asistencia (regla `ON DELETE RESTRICT`).
- Cada operación (crear, editar, desactivar, eliminar) se guarda junto con su
  entrada de bitácora **en la misma transacción** de la base de datos.
- Contraseñas almacenadas como hash bcrypt con sal (nunca en texto plano).
- Un marcaje por empleado y fecha (restricción `UNIQUE`).

Nota: los roles identifican al usuario en pantalla, pero esta fase no
implementa restricción de operaciones por rol.

## Pruebas

```bash
python tests/test_models.py
```

Ejecuta 18 pruebas de lógica de negocio sobre una base temporal aislada
(nunca toca `biocontrol.db`): autenticación correcta e incorrecta, CRUD,
validaciones, bitácora, reglas de borrado y persistencia.

## Nota sobre la biometría

Las plantillas de huellas cargadas son **datos ficticios de prueba**. La
integración real con el lector biométrico no forma parte de esta entrega.
