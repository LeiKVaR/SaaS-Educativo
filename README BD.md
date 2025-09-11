-- Crear base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS SaaS;
USE SaaS;

-- Tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    membership ENUM('FREE', 'PREMIUM') DEFAULT 'FREE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de documentos (archivos importados o creados)
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    drive_file_id VARCHAR(200) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type ENUM('PDF', 'EXCEL', 'DOC') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabla de filas de Excel importados
CREATE TABLE excel_rows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    numero_fila INT NOT NULL,
    data JSON NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- (Opcional) Tabla para guardar JWT activos/invalidados
CREATE TABLE auth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- (Opcional) Historial de cambios de membresía
CREATE TABLE memberships_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    old_plan ENUM('FREE','PREMIUM'),
    new_plan ENUM('FREE','PREMIUM'),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
