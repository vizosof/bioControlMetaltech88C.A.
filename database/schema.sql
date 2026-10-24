-- ============================================================
-- BioControl - Fase 1 | Esquema de base de datos (SQLite)
-- Corregido y validado
-- Nota: PRAGMA foreign_keys aplica por conexión; la aplicación
-- debe volver a ejecutarlo al abrir cada conexión.
-- ============================================================

PRAGMA foreign_keys = ON;

-- 1. Tabla de Roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_rol TEXT UNIQUE NOT NULL
);

-- 2. Tabla de Usuarios del Sistema (acceso al panel)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol_id INTEGER NOT NULL,
    FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE RESTRICT
);

-- 3. Tabla de Empleados
CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL,
    foto_path TEXT,
    estado TEXT NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

-- 4. Tabla de Huellas Dactilares (plantillas - datos ficticios de prueba)
CREATE TABLE IF NOT EXISTS huellas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER NOT NULL,
    plantilla_cifrada TEXT NOT NULL,
    FOREIGN KEY (empleado_id) REFERENCES empleados (id) ON DELETE CASCADE
);

-- 5. Tabla de Parámetros de Jornada
CREATE TABLE IF NOT EXISTS parametros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descripcion TEXT
);

-- 6. Tabla de Marcajes (entrada/salida y cálculo de horas)
-- Regla adoptada: un marcaje por empleado y fecha (modelo de resumen
-- diario). No contempla salidas intermedias ni turnos partidos.
-- ON DELETE RESTRICT: el historial de asistencia impide eliminar al
-- empleado; primero se desactiva o se eliminan sus marcajes.
CREATE TABLE IF NOT EXISTS marcajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    entrada TEXT,
    salida TEXT,
    horas_trabajadas REAL NOT NULL DEFAULT 0.0,
    horas_extras REAL NOT NULL DEFAULT 0.0,
    estado TEXT NOT NULL DEFAULT 'Normal' CHECK (estado IN ('Normal', 'Incompleto', 'Corregido')),
    FOREIGN KEY (empleado_id) REFERENCES empleados (id) ON DELETE RESTRICT,
    UNIQUE (empleado_id, fecha)
);

-- 7. Tabla de Auditoría / Bitácora
-- entidad y registro_id identifican sobre qué tabla y registro actuó el usuario.
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_responsable TEXT NOT NULL,
    accion TEXT NOT NULL,
    entidad TEXT,
    registro_id INTEGER,
    detalles TEXT NOT NULL,
    fecha_hora TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
