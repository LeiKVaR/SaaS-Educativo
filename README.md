# SaaS Google Drive - Documentación Completa

## 📋 Descripción del Proyecto

SaaS Google Drive es una aplicación web desarrollada en Django que permite a los usuarios crear, gestionar e importar documentos de Google Drive. La aplicación incluye un sistema de autenticación JWT, manejo de membresías (FREE/PREMIUM) y integración completa con Google Drive API.

## 🏗️ Arquitectura del Proyecto

```
SaaS/
├── SaaS/                          # Aplicación principal Django
│   ├── models.py                  # Modelos de datos (User, Document, etc.)
│   ├── views.py                   # Vistas de autenticación
│   ├── drive_views.py             # Vistas para Google Drive
│   ├── admin_views.py             # Vistas de administración
│   ├── google_drive_service.py    # Servicio de Google Drive API
│   ├── utils.py                   # Utilidades (JWT, decoradores)
│   └── urls.py                    # URLs de la aplicación
├── config/                        # Configuración del proyecto
│   ├── settings.py                # Configuración Django
│   ├── urls.py                    # URLs principales
│   └── google_credentials.json    # Credenciales Google (no commitear)
├── templates/                     # Plantillas HTML
│   ├── Home.html                  # Página principal
│   ├── Login.html                 # Página de login
│   └── Register.html              # Página de registro
├── static/                        # Archivos estáticos
│   └── style.css                  # Estilos CSS
└── requirements.txt               # Dependencias Python
```

## 🚀 Instalación y Configuración

### 1. Requisitos Previos
- Python 3.8+
- MySQL/MariaDB
- Cuenta de Google Cloud Platform

### 2. Instalación
```bash
# Clonar el repositorio
git clone [url-del-repo]
cd SaaS

# Crear entorno virtual
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Google Drive API

1. **Crear proyecto en Google Cloud Console:**
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un nuevo proyecto
   - Habilita Google Drive API

2. **Crear Service Account:**
   - Ve a IAM & Admin > Service Accounts
   - Crea un nuevo Service Account
   - Descarga el archivo JSON de credenciales
   - Guárdalo como `config/google_credentials.json`

3. **Configurar permisos:**
   - Asigna rol "Editor" al Service Account
   - Asegúrate de que tenga acceso a Google Drive API

### 4. Configuración de Base de Datos
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 5. Ejecutar la aplicación
```bash
python manage.py runserver
```

## 📊 Modelos de Datos

### User (Usuario personalizado)
```python
- email: EmailField (único)
- username: CharField
- created_at: DateTimeField
- updated_at: DateTimeField
```

### MembershipHistory (Historial de membresías)
```python
- user: ForeignKey(User)
- membership_type: CharField (FREE/PREMIUM)
- started_at: DateTimeField
- ended_at: DateTimeField
- is_active: BooleanField
```

### Document (Documentos)
```python
- user: ForeignKey(User)
- title: CharField
- document_type: CharField (PDF/EXCEL/GDOC/GSHEET/GSLIDES)
- google_drive_id: CharField
- google_drive_url: URLField
- file_size: BigIntegerField
- imported_at: DateTimeField
- is_processed: BooleanField
```

### ExcelRow (Filas de Excel)
```python
- document: ForeignKey(Document)
- row_number: IntegerField
- data: JSONField
- created_at: DateTimeField
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/profile` - Perfil del usuario

### Google Drive
- `POST /api/drive/create-doc` - Crear documento
- `GET /api/drive/list-files` - Listar archivos del usuario
- `GET /api/drive/list-google-files` - Explorar Google Drive
- `POST /api/drive/import-file/<file_id>` - Importar archivo (PREMIUM)

### Documentos
- `GET /api/documents` - Listar documentos del usuario
- `GET /api/documents/<id>/rows` - Ver filas de Excel

### Administración
- `GET /api/admin/users` - Listar usuarios
- `POST /api/admin/users/<id>/membership` - Cambiar membresía

## 🛠️ Componentes Principales

### GoogleDriveService
Servicio principal para interactuar con Google Drive API:

**Métodos principales:**
- `setup_service()` - Configura credenciales
- `create_document_with_type()` - Crea documentos (Docs/Sheets/Slides)
- `list_files()` - Lista archivos de Drive
- `import_file_to_system()` - Importa archivos al sistema
- `process_excel_file()` - Procesa archivos Excel

**Características:**
- Manejo automático de credenciales desde múltiples fuentes
- Soporte para diferentes tipos de documentos
- Manejo de errores y logging detallado

### Sistema de Autenticación JWT
- Tokens JWT para autenticación stateless
- Decoradores `@jwt_required` y `@premium_required`
- Manejo automático de expiración de tokens

### Sistema de Membresías
- **FREE**: Acceso básico (crear documentos)
- **PREMIUM**: Acceso completo (importar archivos)

## 🎨 Frontend

### Tecnologías
- HTML5 + CSS3
- JavaScript vanilla
- Diseño responsive
- Interfaz moderna con feedback visual

### Características
- Formularios para crear documentos personalizados
- Listado de archivos con acciones
- Manejo de errores con mensajes claros
- Navegación intuitiva entre secciones

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Credenciales Google (alternativa al archivo JSON)
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Email para domain-wide delegation (opcional)
GOOGLE_IMPERSONATE_EMAIL=usuario@dominio.com
```

### Configuración de Django
```python
# settings.py
GOOGLE_CREDENTIALS = {...}  # Dict con credenciales
SECRET_KEY = 'tu-secret-key'
DEBUG = False  # En producción
ALLOWED_HOSTS = ['tu-dominio.com']
```

## 🚨 Solución de Problemas Comunes

### Error "Invalid JWT Signature"
1. Verificar que las credenciales sean válidas
2. Sincronizar hora del sistema
3. Regenerar credenciales en Google Cloud Console

### Error "Storage quota exceeded"
1. Liberar espacio en Google Drive
2. Vaciar papelera de Google Drive
3. Crear nuevo Service Account si es necesario

### Error de importación duplicada
- El sistema previene importar el mismo archivo múltiples veces por usuario

## 📝 Scripts de Utilidad

### Diagnóstico de Credenciales
```bash
python test_google_credentials.py
```
Verifica que las credenciales de Google funcionen correctamente.

## 🔒 Seguridad

- Autenticación JWT con expiración
- Validación de permisos por endpoint
- Manejo seguro de credenciales
- Protección CSRF en formularios

## 📈 Funcionalidades Principales

1. **Crear Documentos**: Google Docs, Sheets y Slides
2. **Gestión de Archivos**: Listar y organizar documentos
3. **Importación**: Importar archivos existentes (Premium)
4. **Procesamiento Excel**: Extraer y visualizar datos
5. **Sistema de Usuarios**: Registro, login y membresías
6. **Panel Admin**: Gestión de usuarios y membresías

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Añade tests si es necesario
5. Crea un Pull Request