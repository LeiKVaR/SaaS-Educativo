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
        """Configura el servicio de Google Drive"""
        try:
            # Para esta práctica, necesitarás crear un Service Account
            # y descargar el archivo JSON de credenciales
            credentials_path = os.path.join(settings.BASE_DIR, 'google_credentials.json')
            
            if os.path.exists(credentials_path):
                self.credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=self.credentials)
            else:
                print("⚠️  Archivo de credenciales de Google no encontrado")
                print("   Crea un Service Account y descarga google_credentials.json")
                
        except Exception as e:
            print(f"Error configurando Google Drive: {e}")
    
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
