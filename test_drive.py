from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "config/google_credentials.json"

# Cargar credenciales
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Construir el servicio
drive_service = build("drive", "v3", credentials=credentials)

# Ejemplo: listar 10 archivos
results = drive_service.files().list(
    pageSize=10, fields="files(id, name)"
).execute()
items = results.get("files", [])

if not items:
    print("No se encontraron archivos.")
else:
    for item in items:
        print(f"{item['name']} ({item['id']})")
