CREATE DATABASE IF NOT EXISTS luis_barber;
USE luis_barber;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(40) NOT NULL DEFAULT 'cliente'
);

CREATE TABLE IF NOT EXISTS servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    duracion_minutos INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    destacado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    servicio_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    comentarios TEXT,
    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
    creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id)
);

INSERT INTO servicios (nombre, categoria, descripcion, precio, duracion_minutos, activo, destacado)
VALUES
('Corte clasico', 'Cabello', 'Corte limpio con maquina y tijera, terminado con peinado.', 180.00, 35, TRUE, TRUE),
('Fade premium', 'Cabello', 'Degradado personalizado con perfilado de contornos.', 230.00, 45, TRUE, TRUE),
('Barba completa', 'Barba', 'Arreglo de barba con navaja, toalla caliente y aceite.', 140.00, 25, TRUE, FALSE),
('Corte y barba', 'Paquete', 'Servicio completo de corte, barba y peinado final.', 320.00, 60, TRUE, TRUE);
