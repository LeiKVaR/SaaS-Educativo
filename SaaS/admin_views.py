import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from .models import User, MembershipHistory
from .utils import jwt_required, get_user_membership

@csrf_exempt
@require_http_methods(["POST"])
def change_membership(request, user_id):
    """Cambiar membresía de un usuario - Para administradores"""
    try:
        data = json.loads(request.body)
        new_membership = data.get('membership_type')
        
        if new_membership not in ['FREE', 'PREMIUM']:
            return JsonResponse({
                'error': 'Tipo de membresía inválido. Debe ser FREE o PREMIUM',
                'code': 'INVALID_MEMBERSHIP'
            }, status=400)
        
        # Buscar usuario
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'Usuario no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=404)
        
        # Obtener membresía actual
        current_membership = get_user_membership(user)
        
        if current_membership == new_membership:
            return JsonResponse({
                'error': f'El usuario ya tiene membresía {new_membership}',
                'code': 'SAME_MEMBERSHIP'
            }, status=400)
        
        # Desactivar membresía actual
        current_membership_obj = MembershipHistory.objects.filter(
            user=user, 
            is_active=True
        ).first()
        
        if current_membership_obj:
            current_membership_obj.is_active = False
            current_membership_obj.save()
        
        # Crear nueva membresía
        new_membership_obj = MembershipHistory.objects.create(
            user=user,
            membership_type=new_membership,
            is_active=True
        )
        
        return JsonResponse({
            'message': f'Membresía de {user.email} cambiada de {current_membership} a {new_membership}',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'previous_membership': current_membership,
                'new_membership': new_membership
            }
        })
        
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

@require_http_methods(["GET"])
def list_users(request):
    """Listar todos los usuarios con sus membresías"""
    try:
        users = User.objects.all().order_by('-created_at')
        
        users_data = []
        for user in users:
            membership = get_user_membership(user)
            users_data.append({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'membership': membership,
                'created_at': user.created_at.isoformat(),
                'documents_count': user.documents.count()
            })
        
        return JsonResponse({
            'message': f'Se encontraron {len(users_data)} usuarios',
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)
