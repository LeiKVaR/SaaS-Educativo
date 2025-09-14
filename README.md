# SaaS Backend - Sistema de Gestión de Documentos con Google Drive

Este es un sistema backend desarrollado en Django que permite la gestión de documentos importados desde Google Drive, con sistema de autenticación JWT y membresías (FREE/PREMIUM).

## 🚀 Características

- **Autenticación JWT**: Sistema de login/registro con tokens JWT
- **Membresías**: Sistema de membresías FREE y PREMIUM
- **Google Drive Integration**: Importación de archivos PDF y Excel desde Google Drive
- **Procesamiento de Datos**: Extracción y almacenamiento de datos de archivos Excel
- **API REST**: Endpoints para todas las funcionalidades

## 📋 Requisitos Previos

- Python 3.8+
- MySQL 5.7+
- Cuenta de Google Cloud Platform (para Google Drive API)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd MODULO-1-Y-2-TRABAJO-DE-BACKENDS
```

### 2. Crear entorno virtual
```bash
python -m venv env
# En Windows:
env\Scripts\activate
# En Linux/Mac:
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos MySQL
1. Crear una base de datos llamada `SaaS` en MySQL
2. Configurar las credenciales en `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'SaaS',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Configurar Google Drive API
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar la Google Drive API
4. Crear una Service Account
5. Descargar el archivo JSON de credenciales
6. Renombrar el archivo a `google_credentials.json` y colocarlo en la raíz del proyecto

### 6. Aplicar migraciones
```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor
```bash
python manage.py runserver
```

## 📚 Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/profile` - Perfil del usuario (requiere JWT)

### Google Drive
- `POST /api/drive/create-doc` - Crear Google Doc (requiere JWT)
- `GET /api/drive/list-files` - Listar archivos de Drive (requiere JWT)
- `POST /api/drive/import-file/<file_id>` - Importar archivo (requiere JWT + PREMIUM)

### Documentos
- `GET /api/documents` - Listar documentos del usuario (requiere JWT)
- `GET /api/documents/<id>/rows` - Obtener filas de Excel (requiere JWT)

### Administración
- `GET /api/admin/users` - Listar usuarios
- `POST /api/admin/users/<id>/membership` - Cambiar membresía

## 🔐 Autenticación

El sistema usa JWT (JSON Web Tokens) para la autenticación. Incluye el token en el header:

```
Authorization: Bearer <tu_token_jwt>
```

## 📊 Modelos de Datos

### User
- Usuario personalizado con email como username
- Campos: email, username, created_at, updated_at

### MembershipHistory
- Historial de membresías del usuario
- Tipos: FREE, PREMIUM

### Document
- Documentos importados desde Google Drive
- Tipos: PDF, EXCEL, GDOC

### ExcelRow
- Filas de datos extraídas de archivos Excel
- Almacena datos como JSON

### AuthToken
- Tokens JWT para autenticación
- Control de expiración y validez

## 🎯 Funcionalidades por Membresía

### FREE
- Registro y login
- Crear Google Docs
- Listar archivos de Drive
- Ver documentos propios
- Ver filas de Excel propios

### PREMIUM
- Todas las funcionalidades FREE
- Importar archivos de Drive al sistema
- Procesamiento completo de archivos Excel

## 🐛 Solución de Problemas

### Error de credenciales de Google
Si ves el error sobre credenciales de Google, asegúrate de:
1. Tener el archivo `google_credentials.json` en la raíz del proyecto
2. Que el archivo tenga credenciales válidas de Service Account
3. Que la Service Account tenga permisos para Google Drive API

### Error de conexión a MySQL
Verifica que:
1. MySQL esté ejecutándose
2. La base de datos `SaaS` exista
3. Las credenciales en `settings.py` sean correctas

## 📝 Notas de Desarrollo

- El proyecto está configurado para desarrollo (DEBUG=True)
- Para producción, cambiar DEBUG=False y configurar ALLOWED_HOSTS
- Las credenciales de Google Drive son necesarias para las funcionalidades de Drive
- El sistema maneja errores graciosamente cuando Google Drive no está configurado

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
