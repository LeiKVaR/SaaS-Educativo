#!/usr/bin/env python3
"""
Script de diagnóstico para verificar credenciales de Google Drive
"""
import os
import json
import sys
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def test_credentials():
    """Prueba las credenciales de Google Drive paso a paso"""
    print("🔍 Diagnóstico de credenciales de Google Drive")
    print("=" * 50)
    
    # 1. Verificar archivo de credenciales
    credentials_path = os.path.join(os.path.dirname(__file__), 'config', 'google_credentials.json')
    print(f"📁 Buscando credenciales en: {credentials_path}")
    
    if not os.path.exists(credentials_path):
        print("❌ Archivo de credenciales no encontrado")
        return False
    
    print("✅ Archivo de credenciales encontrado")
    
    # 2. Verificar formato JSON
    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            creds_data = json.load(f)
        print("✅ Archivo JSON válido")
    except json.JSONDecodeError as e:
        print(f"❌ Error en formato JSON: {e}")
        return False
    
    # 3. Verificar campos requeridos
    required_fields = ['type', 'project_id', 'private_key', 'client_email']
    missing_fields = [field for field in required_fields if field not in creds_data]
    
    if missing_fields:
        print(f"❌ Campos faltantes: {missing_fields}")
        return False
    
    print("✅ Todos los campos requeridos presentes")
    
    # 4. Verificar tipo de cuenta
    if creds_data.get('type') != 'service_account':
        print(f"❌ Tipo de cuenta incorrecto: {creds_data.get('type')}")
        return False
    
    print("✅ Tipo de cuenta correcto (service_account)")
    
    # 5. Verificar formato de clave privada
    private_key = creds_data.get('private_key', '')
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("❌ Formato de clave privada incorrecto")
        return False
    
    print("✅ Formato de clave privada correcto")
    
    # 6. Verificar hora del sistema
    print(f"🕐 Hora actual del sistema: {datetime.now()}")
    
    # 7. Intentar crear credenciales
    try:
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(creds_data, scopes=scopes)
        print("✅ Credenciales creadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando credenciales: {e}")
        return False
    
    # 8. Intentar construir servicio
    try:
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Servicio de Google Drive construido")
    except Exception as e:
        print(f"❌ Error construyendo servicio: {e}")
        return False
    
    # 9. Probar conexión real
    try:
        print("🔄 Probando conexión con Google Drive...")
        # Intentar listar archivos (solo metadatos, sin contenido)
        results = service.files().list(pageSize=1, fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"✅ Conexión exitosa - Se pueden acceder a {len(files)} archivo(s)")
        return True
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        
        # Diagnóstico específico para errores comunes
        error_str = str(e)
        if 'invalid_grant' in error_str.lower():
            print("\n🔧 DIAGNÓSTICO ESPECÍFICO:")
            print("   - Error 'invalid_grant' indica problema con las credenciales")
            print("   - Posibles causas:")
            print("     1. Clave privada corrupta o regenerada")
            print("     2. Hora del sistema desincronizada")
            print("     3. Service Account deshabilitado")
            print("     4. Credenciales revocadas en Google Cloud Console")
        
        return False

def show_solutions():
    """Muestra soluciones para problemas comunes"""
    print("\n🛠️  SOLUCIONES RECOMENDADAS:")
    print("=" * 50)
    print("1. REGENERAR CREDENCIALES:")
    print("   - Ve a Google Cloud Console")
    print("   - Navega a IAM & Admin > Service Accounts")
    print("   - Encuentra tu service account")
    print("   - Crea una nueva clave JSON")
    print("   - Reemplaza el archivo google_credentials.json")
    
    print("\n2. VERIFICAR PERMISOS:")
    print("   - Asegúrate de que el Service Account tenga permisos de Google Drive API")
    print("   - Verifica que la API de Google Drive esté habilitada")
    
    print("\n3. SINCRONIZAR HORA:")
    print("   - En Windows: Ejecuta 'w32tm /resync' como administrador")
    print("   - O ve a Configuración > Hora e idioma > Sincronizar reloj")
    
    print("\n4. VERIFICAR ESTADO DEL SERVICE ACCOUNT:")
    print("   - En Google Cloud Console, verifica que esté habilitado")
    print("   - Revisa que no haya sido eliminado o deshabilitado")

if __name__ == "__main__":
    success = test_credentials()
    
    if not success:
        show_solutions()
        sys.exit(1)
    else:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("Las credenciales están funcionando correctamente.")
