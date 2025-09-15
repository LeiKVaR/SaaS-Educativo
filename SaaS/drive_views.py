import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils import jwt_required, premium_required, get_user_membership
from .google_drive_service import drive_service
from .models import Document, ExcelRow

@jwt_required
@csrf_exempt
@require_http_methods(["POST"])
def create_document(request):
    """Crear un nuevo Google Doc - Disponible para todos los usuarios"""
    try:
        data = json.loads(request.body) if request.body else {}
        title = data.get('title', f'Documento de {request.user.username}')
        
        # Crear documento en Google Drive
        doc_result, error = drive_service.create_document(title)
        
        if error:
            return JsonResponse({
                'error': error,
                'code': 'DRIVE_ERROR'
            }, status=500)
        
        # Registrar documento en la base de datos
        document = Document.objects.create(
            user=request.user,
            title=title,
            document_type='GDOC',
            google_drive_id=doc_result['id'],
            google_drive_url=doc_result['url'],
            is_processed=True
        )
        
        return JsonResponse({
            'message': f'Se creó un Google Doc con ID {doc_result["id"]}',
            'document': {
                'id': document.id,
                'google_drive_id': doc_result['id'],
                'title': title,
                'url': doc_result['url'],
                'type': 'GDOC'
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)

@jwt_required
@require_http_methods(["GET"])
def list_files(request):
    """Listar archivos creados o importados por el usuario (multi-tenant)"""
    try:
        documents = Document.objects.filter(user=request.user)

        files = []
        for doc in documents:
            doc_info = {
                "id": doc.id,
                "title": doc.title,
                "type": doc.document_type,
                "google_drive_id": doc.google_drive_id,
                "google_drive_url": doc.google_drive_url,
                "imported_at": doc.imported_at.isoformat() if doc.imported_at else None,
                "is_processed": doc.is_processed,
            }

            # Si es Excel, agregar cantidad de filas procesadas
            if doc.document_type == "EXCEL":
                doc_info["rows_count"] = doc.excel_rows.count()

            files.append(doc_info)

        return JsonResponse({
            "message": f"Se encontraron {len(files)} archivos para el usuario {request.user.username}",
            "files": files,
        })

    except Exception as e:
        return JsonResponse({
            "error": f"Error interno: {str(e)}",
            "code": "INTERNAL_ERROR"
        }, status=500)

@jwt_required
@premium_required
@csrf_exempt
@require_http_methods(["POST"])
def import_file(request, file_id):
    """Importar archivo de Google Drive al sistema - Solo usuarios PREMIUM"""
    try:
        # Verificar si el archivo ya fue importado por este usuario
        existing_doc = Document.objects.filter(
            user=request.user,
            google_drive_id=file_id
        ).first()
        
        if existing_doc:
            return JsonResponse({
                'error': 'Este archivo ya fue importado anteriormente',
                'code': 'ALREADY_IMPORTED',
                'document_id': existing_doc.id
            }, status=400)
        
        # Importar archivo
        result, error = drive_service.import_file_to_system(file_id, request.user)
        
        if error:
            return JsonResponse({
                'error': error,
                'code': 'IMPORT_ERROR'
            }, status=500)
        
        document = result['document']
        response_data = {
            'message': f'Archivo {document.title} importado exitosamente',
            'document': {
                'id': document.id,
                'title': document.title,
                'type': document.document_type,
                'google_drive_id': document.google_drive_id,
                'google_drive_url': document.google_drive_url,
                'imported_at': document.imported_at.isoformat(),
                'is_processed': document.is_processed
            }
        }
        
        # Agregar información específica según el tipo
        if result['type'] == 'EXCEL':
            response_data['rows_processed'] = result['rows_processed']
            response_data['message'] += f' - {result["rows_processed"]} filas procesadas'
        
        return JsonResponse(response_data, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)

@jwt_required
@require_http_methods(["GET"])
def list_user_documents(request):
    """Listar documentos importados por el usuario"""
    try:
        documents = Document.objects.filter(user=request.user)
        
        docs_data = []
        for doc in documents:
            doc_info = {
                'id': doc.id,
                'title': doc.title,
                'type': doc.document_type,
                'google_drive_id': doc.google_drive_id,
                'google_drive_url': doc.google_drive_url,
                'imported_at': doc.imported_at.isoformat(),
                'is_processed': doc.is_processed
            }
            
            # Agregar conteo de filas para Excel
            if doc.document_type == 'EXCEL':
                doc_info['rows_count'] = doc.excel_rows.count()
            
            docs_data.append(doc_info)
        
        return JsonResponse({
            'message': f'Se encontraron {len(docs_data)} documentos',
            'documents': docs_data,
            'user_membership': get_user_membership(request.user)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)

@jwt_required
@require_http_methods(["GET"])
def get_document_rows(request, document_id):
    """Obtener filas de un documento Excel - Disponible para todos los usuarios"""
    try:
        # Verificar que el documento pertenece al usuario
        try:
            document = Document.objects.get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            return JsonResponse({
                'error': 'Documento no encontrado',
                'code': 'DOCUMENT_NOT_FOUND'
            }, status=404)
        
        if document.document_type != 'EXCEL':
            return JsonResponse({
                'error': 'Este documento no es un archivo Excel',
                'code': 'NOT_EXCEL_FILE'
            }, status=400)
        
        # Obtener filas del Excel
        rows = ExcelRow.objects.filter(document=document).order_by('row_number')
        
        rows_data = []
        for row in rows:
            rows_data.append({
                'row_number': row.row_number,
                'data': row.data,
                'created_at': row.created_at.isoformat()
            })
        
        return JsonResponse({
            'message': f'Documento: {document.title}',
            'document': {
                'id': document.id,
                'title': document.title,
                'type': document.document_type,
                'imported_at': document.imported_at.isoformat()
            },
            'rows_count': len(rows_data),
            'rows': rows_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)
