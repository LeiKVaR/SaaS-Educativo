# 📋 Documentación de Endpoints - SaaS con Google Drive

## 🔧 Configuración Inicial

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Google Drive API
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la Google Drive API
4. Crea un Service Account
5. Descarga el archivo JSON de credenciales
6. Renómbralo a `google_credentials.json` y colócalo en la raíz del proyecto

### 3. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Autenticación

### 1. Registrar Usuario
- **URL:** `POST http://localhost:8000/api/auth/register`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
    "email": "usuario@ejemplo.com",
    "password": "mipassword123",
    "username": "usuario1"
}
```
- **Respuesta exitosa:**
```json
{
    "message": "Usuario registrado exitosamente",
    "user": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "username": "usuario1",
        "membership": "FREE"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Iniciar Sesión
- **URL:** `POST http://localhost:8000/api/auth/login`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
    "email": "usuario@ejemplo.com",
    "password": "mipassword123"
}
```
- **Respuesta exitosa:**
```json
{
    "message": "Inicio de sesión exitoso",
    "user": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "username": "usuario1",
        "membership": "FREE"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Ver Perfil
- **URL:** `GET http://localhost:8000/api/auth/profile`
- **Headers:** 
  - `Authorization: Bearer {token}`
- **Respuesta exitosa:**
```json
{
    "user": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "username": "usuario1",
        "membership": "FREE",
        "created_at": "2024-01-15T10:30:00Z",
        "documents_count": 0
    }
}
```

---

## 📁 Google Drive

### 4. Crear Google Doc
- **URL:** `POST http://localhost:8000/api/drive/create-doc`
- **Headers:** 
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`
- **Body:**
```json
{
    "title": "Mi Nuevo Documento"
}
```
- **Respuesta exitosa:**
```json
{
    "message": "Se creó un Google Doc con ID 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "document": {
        "id": 1,
        "google_drive_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        "title": "Mi Nuevo Documento",
        "url": "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit",
        "type": "GDOC"
    }
}
```

### 5. Listar Archivos de Drive
- **URL:** `GET http://localhost:8000/api/drive/list-files`
- **Headers:** 
  - `Authorization: Bearer {token}`
- **Respuesta exitosa:**
```json
{
    "message": "Se encontraron 3 archivos",
    "files": [
        {
            "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "name": "Estudiantes.xlsx",
            "type": "EXCEL",
            "size": 15420,
            "modified": "2024-01-15T09:00:00Z"
        },
        {
            "id": "1mGcZ8vLRjVQpB9FO7QjpQpB9FO7QjpQpB9FO7Qjp",
            "name": "Manual.pdf",
            "type": "PDF",
            "size": 2048000,
            "modified": "2024-01-14T15:30:00Z"
        }
    ],
    "user_membership": "FREE"
}
```

### 6. Importar Archivo (Solo PREMIUM)
- **URL:** `POST http://localhost:8000/api/drive/import-file/{file_id}`
- **Headers:** 
  - `Authorization: Bearer {token}`
- **Ejemplo:** `POST http://localhost:8000/api/drive/import-file/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**Para usuario FREE (Error esperado):**
```json
{
    "error": "Necesitas membresía Premium para acceder a esta funcionalidad",
    "code": "PREMIUM_REQUIRED",
    "current_membership": "FREE"
}
```

**Para usuario PREMIUM (Éxito):**
```json
{
    "message": "Archivo Estudiantes.xlsx importado exitosamente - 25 filas procesadas",
    "document": {
        "id": 2,
        "title": "Estudiantes.xlsx",
        "type": "EXCEL",
        "google_drive_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        "google_drive_url": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view",
        "imported_at": "2024-01-15T11:00:00Z",
        "is_processed": true
    },
    "rows_processed": 25
}
```

---

## 📄 Documentos

### 7. Listar Documentos del Usuario
- **URL:** `GET http://localhost:8000/api/documents`
- **Headers:** 
  - `Authorization: Bearer {token}`
- **Respuesta exitosa:**
```json
{
    "message": "Se encontraron 2 documentos",
    "documents": [
        {
            "id": 1,
            "title": "Mi Nuevo Documento",
            "type": "GDOC",
            "google_drive_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "google_drive_url": "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit",
            "imported_at": "2024-01-15T10:45:00Z",
            "is_processed": true
        },
        {
            "id": 2,
            "title": "Estudiantes.xlsx",
            "type": "EXCEL",
            "google_drive_id": "1mGcZ8vLRjVQpB9FO7QjpQpB9FO7QjpQpB9FO7Qjp",
            "google_drive_url": "https://drive.google.com/file/d/1mGcZ8vLRjVQpB9FO7QjpQpB9FO7QjpQpB9FO7Qjp/view",
            "imported_at": "2024-01-15T11:00:00Z",
            "is_processed": true,
            "rows_count": 25
        }
    ],
    "user_membership": "PREMIUM"
}
```

### 8. Ver Filas de Excel
- **URL:** `GET http://localhost:8000/api/documents/{document_id}/rows`
- **Headers:** 
  - `Authorization: Bearer {token}`
- **Ejemplo:** `GET http://localhost:8000/api/documents/2/rows`
- **Respuesta exitosa:**
```json
{
    "message": "Documento: Estudiantes.xlsx",
    "document": {
        "id": 2,
        "title": "Estudiantes.xlsx",
        "type": "EXCEL",
        "imported_at": "2024-01-15T11:00:00Z"
    },
    "rows_count": 3,
    "rows": [
        {
            "row_number": 1,
            "data": {
                "Nombre": "Juan Pérez",
                "Edad": 20,
                "Calificación": 85,
                "Curso": "Matemáticas"
            },
            "created_at": "2024-01-15T11:00:01Z"
        },
        {
            "row_number": 2,
            "data": {
                "Nombre": "María García",
                "Edad": 19,
                "Calificación": 92,
                "Curso": "Física"
            },
            "created_at": "2024-01-15T11:00:02Z"
        }
    ]
}
```

---

## 👥 Administración

### 9. Listar Usuarios (Admin)
- **URL:** `GET http://localhost:8000/api/admin/users`
- **Respuesta exitosa:**
```json
{
    "message": "Se encontraron 2 usuarios",
    "users": [
        {
            "id": 1,
            "email": "usuario@ejemplo.com",
            "username": "usuario1",
            "membership": "FREE",
            "created_at": "2024-01-15T10:30:00Z",
            "documents_count": 1
        },
        {
            "id": 2,
            "email": "premium@ejemplo.com",
            "username": "premium1",
            "membership": "PREMIUM",
            "created_at": "2024-01-15T09:15:00Z",
            "documents_count": 3
        }
    ]
}
```

### 10. Cambiar Membresía (Admin)
- **URL:** `POST http://localhost:8000/api/admin/users/{user_id}/membership`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
    "membership_type": "PREMIUM"
}
```
- **Ejemplo:** `POST http://localhost:8000/api/admin/users/1/membership`
- **Respuesta exitosa:**
```json
{
    "message": "Membresía de usuario@ejemplo.com cambiada de FREE a PREMIUM",
    "user": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "username": "usuario1",
        "previous_membership": "FREE",
        "new_membership": "PREMIUM"
    }
}
```

---

## 🧪 Flujo de Pruebas Completo

### Paso 1: Configuración
1. Registrar usuario → obtener token
2. Verificar que es FREE por defecto

### Paso 2: Funcionalidades básicas (FREE)
1. Crear Google Doc ✅
2. Listar archivos de Drive ✅
3. Intentar importar archivo ❌ (debe fallar)
4. Ver documentos propios ✅

### Paso 3: Upgrade a PREMIUM
1. Cambiar membresía a PREMIUM (admin)
2. Verificar cambio en perfil

### Paso 4: Funcionalidades PREMIUM
1. Importar archivo Excel ✅
2. Importar archivo PDF ✅
3. Ver filas del Excel ✅
4. Listar documentos (ahora con más archivos) ✅

---

## ⚠️ Códigos de Error Comunes

- `TOKEN_MISSING` (401): Falta el header Authorization
- `TOKEN_EXPIRED` (401): Token expirado
- `PREMIUM_REQUIRED` (403): Funcionalidad solo para PREMIUM
- `DRIVE_ERROR` (500): Error con Google Drive API
- `DOCUMENT_NOT_FOUND` (404): Documento no existe
- `ALREADY_IMPORTED` (400): Archivo ya importado

---

## 🚀 Notas Importantes

1. **Token JWT**: Guarda el token del login y úsalo en todas las peticiones autenticadas
2. **Google Drive**: Necesitas configurar las credenciales antes de usar funciones de Drive
3. **Membresías**: Solo usuarios PREMIUM pueden importar archivos
4. **Excel**: Los archivos Excel se procesan automáticamente y se guardan fila por fila
5. **PDF**: Los archivos PDF solo se registran (no se procesan el contenido)
