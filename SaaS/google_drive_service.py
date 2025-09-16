import os
import io
import json
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from django.conf import settings
from .models import Document, ExcelRow

class GoogleDriveService:
    """Servicio para interactuar con Google Drive API"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.setup_service()
    
    def setup_service(self):
        """Configura el servicio de Google Drive con múltiples fuentes de credenciales"""
        try:
            scopes = ['https://www.googleapis.com/auth/drive']

            def load_credentials_info():
                """Intenta cargar el JSON de credenciales desde varias fuentes"""
                # 1) Variable de entorno con el JSON completo
                env_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                if env_json:
                    try:
                        data = json.loads(env_json)
                        return data
                    except Exception:
                        print("⚠️  GOOGLE_CREDENTIALS_JSON no contiene JSON válido")

                # 2) settings.GOOGLE_CREDENTIALS como dict/string
                creds_in_settings = getattr(settings, 'GOOGLE_CREDENTIALS', None)
                if creds_in_settings:
                    try:
                        if isinstance(creds_in_settings, str):
                            return json.loads(creds_in_settings)
                        if isinstance(creds_in_settings, dict):
                            return creds_in_settings
                    except Exception:
                        print("⚠️  settings.GOOGLE_CREDENTIALS no es JSON válido")

                # 3) Archivo en la raíz del proyecto
                candidates = [
                    os.path.join(settings.BASE_DIR, 'google_credentials.json'),
                    os.path.join(settings.BASE_DIR, 'config', 'google_credentials.json'),
                ]

                # 4) Archivo alternativo: toma el primero .json en config/ que sea de tipo service_account
                config_dir = os.path.join(settings.BASE_DIR, 'config')
                if os.path.isdir(config_dir):
                    for name in os.listdir(config_dir):
                        if name.lower().endswith('.json'):
                            candidates.append(os.path.join(config_dir, name))

                for path in candidates:
                    if os.path.exists(path):
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            return data
                        except Exception as e:
                            print(f"⚠️  No se pudo leer {path}: {e}")
                return None

            info = load_credentials_info()
            if not info:
                print("⚠️  No se encontraron credenciales de Google.")
                print("   Provee GOOGLE_CREDENTIALS_JSON, settings.GOOGLE_CREDENTIALS, o un archivo google_credentials.json.")
                self.service = None
                return

            # Validaciones básicas
            if info.get('type') != 'service_account':
                print("⚠️  El JSON de credenciales no es de tipo 'service_account'.")
                self.service = None
                return

            # Soporte opcional para domain-wide delegation si se provee un sujeto
            delegated_subject = getattr(settings, 'GOOGLE_IMPERSONATE_EMAIL', None) or os.getenv('GOOGLE_IMPERSONATE_EMAIL')
            try:
                if delegated_subject:
                    self.credentials = Credentials.from_service_account_info(info, scopes=scopes, subject=delegated_subject)
                else:
                    self.credentials = Credentials.from_service_account_info(info, scopes=scopes)
                self.service = build('drive', 'v3', credentials=self.credentials)
                print("✅ Google Drive API configurado correctamente")
            except Exception as cred_error:
                print("⚠️  Error con las credenciales de Google.")
                print("   Detalle:", cred_error)
                print("   Revisa que la clave privada sea válida y la hora del sistema esté sincronizada.")
                self.service = None

        except Exception as e:
            print(f"Error configurando Google Drive: {e}")
            self.service = None
    
    def reload_service(self):
        """Fuerza la recarga del servicio con nuevas credenciales"""
        self.service = None
        self.credentials = None
        self.setup_service()
        return self.service is not None

    def create_document(self, title="Nuevo Documento"):
        """Crea un nuevo Google Doc"""
        if not self.service:
            return None, "Servicio de Google Drive no configurado"
        
        try:
            # Crear documento
            doc_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            doc = self.service.files().create(body=doc_metadata).execute()
            
            # Hacer el documento público para lectura
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.service.permissions().create(
                fileId=doc['id'],
                body=permission
            ).execute()
            
            return {
                'id': doc['id'],
                'name': doc['name'],
                'url': f"https://docs.google.com/document/d/{doc['id']}/edit"
            }, None
            
        except Exception as e:
            return None, f"Error creando documento: {str(e)}"
    
    def create_document_with_type(self, title="Nuevo Documento", mime_type='application/vnd.google-apps.document'):
        """Crea un nuevo documento de Google con tipo específico"""
        if not self.service:
            return None, "Servicio de Google Drive no configurado"
        
        try:
            # Crear documento
            doc_metadata = {
                'name': title,
                'mimeType': mime_type
            }
            
            doc = self.service.files().create(body=doc_metadata).execute()
            
            # Hacer el documento público para lectura
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.service.permissions().create(
                fileId=doc['id'],
                body=permission
            ).execute()
            
            # Generar URL apropiada según el tipo
            url_patterns = {
                'application/vnd.google-apps.document': f"https://docs.google.com/document/d/{doc['id']}/edit",
                'application/vnd.google-apps.spreadsheet': f"https://docs.google.com/spreadsheets/d/{doc['id']}/edit",
                'application/vnd.google-apps.presentation': f"https://docs.google.com/presentation/d/{doc['id']}/edit"
            }
            
            url = url_patterns.get(mime_type, f"https://drive.google.com/file/d/{doc['id']}/view")
            
            return {
                'id': doc['id'],
                'name': doc['name'],
                'url': url,
                'mimeType': mime_type
            }, None
            
        except Exception as e:
            return None, f"Error creando documento: {str(e)}"
    
    def list_files(self, mime_types=None):
        """Lista archivos de Drive filtrados por tipo MIME"""
        if not self.service:
            return [], "Servicio de Google Drive no configurado"
        
        try:
            # Tipos MIME para Excel y PDF
            if not mime_types:
                mime_types = [
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel
                    'application/vnd.ms-excel',  # Excel legacy
                    'application/pdf'  # PDF
                ]
            
            # Construir query para filtrar por tipos MIME
            mime_query = ' or '.join([f"mimeType='{mime}'" for mime in mime_types])
            query = f"({mime_query}) and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=50,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            # Formatear respuesta
            formatted_files = []
            for file in files:
                file_type = 'EXCEL' if 'spreadsheet' in file['mimeType'] or 'excel' in file['mimeType'] else 'PDF'
                formatted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'type': file_type,
                    'size': int(file.get('size', 0)),
                    'modified': file['modifiedTime']
                })
            
            return formatted_files, None
            
        except Exception as e:
            return [], f"Error listando archivos: {str(e)}"
    
    def download_file(self, file_id):
        """Descarga un archivo de Drive"""
        if not self.service:
            return None, None, "Servicio de Google Drive no configurado"
        
        try:
            # Obtener metadata del archivo
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            # Descargar archivo
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_io.seek(0)
            return file_io, file_metadata, None
            
        except Exception as e:
            return None, None, f"Error descargando archivo: {str(e)}"
    
    def process_excel_file(self, file_io, document):
        """Procesa un archivo Excel y guarda las filas en la base de datos"""
        try:
            # Leer Excel con pandas
            df = pd.read_excel(file_io, engine='openpyxl')
            
            # Limpiar datos NaN
            df = df.fillna('')
            
            # Guardar cada fila en la base de datos
            for index, row in df.iterrows():
                row_data = row.to_dict()
                
                ExcelRow.objects.create(
                    document=document,
                    row_number=index + 1,
                    data=row_data
                )
            
            return len(df), None
            
        except Exception as e:
            return 0, f"Error procesando Excel: {str(e)}"
    
    def import_file_to_system(self, file_id, user):
        """Importa un archivo de Drive al sistema"""
        try:
            # Descargar archivo
            file_io, metadata, error = self.download_file(file_id)
            if error:
                return None, error
            
            # Determinar tipo de archivo
            mime_type = metadata['mimeType']
            if 'spreadsheet' in mime_type or 'excel' in mime_type:
                doc_type = 'EXCEL'
            elif 'pdf' in mime_type:
                doc_type = 'PDF'
            else:
                return None, "Tipo de archivo no soportado"
            
            # Crear registro del documento
            document = Document.objects.create(
                user=user,
                title=metadata['name'],
                document_type=doc_type,
                google_drive_id=file_id,
                google_drive_url=f"https://drive.google.com/file/d/{file_id}/view",
                file_size=int(metadata.get('size', 0))
            )
            
            # Procesar según el tipo
            if doc_type == 'EXCEL':
                rows_count, error = self.process_excel_file(file_io, document)
                if error:
                    document.delete()
                    return None, error
                
                document.is_processed = True
                document.save()
                
                return {
                    'document': document,
                    'rows_processed': rows_count,
                    'type': 'EXCEL'
                }, None
            
            elif doc_type == 'PDF':
                # Para PDF solo registramos el documento
                document.is_processed = True
                document.save()
                
                return {
                    'document': document,
                    'type': 'PDF'
                }, None
            
        except Exception as e:
            return None, f"Error importando archivo: {str(e)}"

# Instancia global del servicio
drive_service = GoogleDriveService()

def get_drive_service():
    """Obtiene una instancia fresca del servicio de Google Drive"""
    global drive_service
    if not drive_service.service:
        drive_service.reload_service()
    return drive_service
