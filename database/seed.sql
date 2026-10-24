-- ============================================================
-- BioControl - Fase 1 | Datos de prueba (seed)
-- Corregido y validado junto con schema.sql
-- Credenciales de demostración (todas con la misma contraseña):
--   admin / biocontrol2026        (Administrador)
--   gerencia / biocontrol2026    (Gerente)
--   supervisor / biocontrol2026
--   consulta / biocontrol2026
--   auditor / biocontrol2026
-- NOTA: los hashes son bcrypt reales; los datos personales son
-- ficticios y las plantillas de huellas son marcadores de prueba.
-- ============================================================

-- 1. Roles
INSERT INTO roles (id, nombre_rol) VALUES
(1, 'Administrador'),
(2, 'Gerente');

-- 2. Usuarios del sistema (hashes bcrypt reales, coste 12)
INSERT INTO usuarios (username, password_hash, rol_id) VALUES
('admin', '$2b$12$LkW6d5vURNbYcVKFsWIbSeTjyjQkn3TMxUyw0d2vuNL7epN81TsfC', 1),
('gerencia', '$2b$12$Q4BPRAOrROizKft1tWKIR.oAUTzTURYqQ6JPt1MXVEfJdzfFORc8a', 2),
('supervisor', '$2b$12$aaj5Vm8.4AdVzr1cjB5Rcuk/45HC1VRE2dRnR9VKJyPRYQYq7X4m2', 1),
('consulta', '$2b$12$fL.Eo3zOrmQ7pd.YHHiI4uDgjB5O9CJe2bgkOmJQYZJCCw4GppakG', 2),
('auditor', '$2b$12$1ZcWljNFvFJLrM20sMGTjOWRLNwCaIkLSpYOG4w1SwOKB5oTIDoJq', 1);

-- 3. Empleados (5 registros)
INSERT INTO empleados (id, cedula, nombre, cargo, foto_path, estado) VALUES
(1, 'V-00.000.001', 'María Pérez', 'Operario de corte', 'assets/fotos/v1.png', 'Activo'),
(2, 'V-00.000.002', 'Luis Rojas', 'Soldadura', 'assets/fotos/v2.png', 'Activo'),
(3, 'V-00.000.003', 'Ana Gómez', 'Administración', 'assets/fotos/v3.png', 'Activo'),
(4, 'V-00.000.004', 'Carlos Díaz', 'Almacén', 'assets/fotos/v4.png', 'Inactivo'),
(5, 'V-00.000.005', 'Pedro Soto', 'Mantenimiento', 'assets/fotos/v5.png', 'Activo');

-- 4. Huellas (plantillas ficticias de prueba)
INSERT INTO huellas (empleado_id, plantilla_cifrada) VALUES
(1, 'TEMPLATE_PRUEBA_A101'),
(2, 'TEMPLATE_PRUEBA_B202'),
(3, 'TEMPLATE_PRUEBA_C303'),
(4, 'TEMPLATE_PRUEBA_D404'),
(5, 'TEMPLATE_PRUEBA_E505');

-- 5. Parámetros de jornada (5 registros)
-- Regla de cálculo del seed (marcajes completos):
-- horas_extras = max(0, horas_trabajadas - 8.0)
INSERT INTO parametros (clave, valor, descripcion) VALUES
('HORAS_JORNADA_ORDINARIA', '8.0', 'Cantidad de horas estándar por jornada diaria laborable.'),
('LIMITE_HORAS_EXTRAS', '4.0', 'Límite interno configurado de horas extras por día.'),
('TOLERANCIA_MINUTOS', '15', 'Minutos de gracia permitidos en la entrada antes de considerarse retraso.'),
('PERIODO_CIERRE_OBRERO', 'Semanal', 'Periodo de cierre de nómina del personal obrero.'),
('PERIODO_CIERRE_ADMIN', 'Quincenal', 'Periodo de cierre de nómina del personal administrativo.');

-- 6. Marcajes (5 registros)
-- Regla de negocio adoptada: en marcajes completos,
-- horas_extras = max(0, horas_trabajadas - 8.0).
-- Los marcajes incompletos no generan horas (0.0).
-- El valor 0.05 del primer registro es una decisión provisional
-- de negocio para los datos de prueba.
INSERT INTO marcajes (empleado_id, fecha, entrada, salida, horas_trabajadas, horas_extras, estado) VALUES
(1, '2026-10-05', '07:02', '15:05', 8.05, 0.05, 'Normal'),
(1, '2026-10-06', '07:00', '17:30', 10.50, 2.50, 'Normal'),
(2, '2026-10-07', '07:10', NULL, 0.0, 0.0, 'Incompleto'),
(2, '2026-10-08', '07:05', '15:00', 7.92, 0.0, 'Corregido'),
(3, '2026-10-08', '08:00', '16:00', 8.00, 0.0, 'Normal');

-- 7. Auditoría / Bitácora (5 registros)
-- usuario_responsable coincide con los username reales de la tabla usuarios.
INSERT INTO auditoria (usuario_responsable, accion, entidad, registro_id, detalles, fecha_hora) VALUES
('admin', 'INICIALIZACION', 'BASE_DATOS', NULL, 'Estructuración inicial de la base de datos.', '2026-10-09 08:00:10'),
('admin', 'REGISTRO', 'EMPLEADOS', NULL, 'Carga de los 5 empleados iniciales.', '2026-10-09 08:05:22'),
('gerencia', 'CONFIGURACION', 'PARAMETROS', NULL, 'Parámetros de jornada ordinaria de 8 horas.', '2026-10-09 09:15:00'),
('admin', 'CORRECCION', 'MARCAJES', 4, 'Salida de Luis Rojas (ID 2) corregida.', '2026-10-08 16:30:45'),
('gerencia', 'CONSULTA', 'REPORTES', NULL, 'Reporte de asistencia del período generado en Excel.', '2026-10-09 11:00:00');
