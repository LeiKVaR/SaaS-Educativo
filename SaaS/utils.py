import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from .models import User, AuthToken, MembershipHistory

def generate_jwt_token(user):
    """Genera un token JWT para el usuario"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': timezone.now() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': timezone.now()
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    
    # Guardar el token en la base de datos
    auth_token = AuthToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    
    return token

def decode_jwt_token(token):
    """Decodifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    """Decorador que requiere autenticación JWT"""
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = None
        
        # Buscar token en el header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return JsonResponse({
                'error': 'Token de acceso requerido',
                'code': 'TOKEN_MISSING'
            }, status=401)
        
        # Verificar token en la base de datos
        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            if auth_token.is_expired():
                auth_token.is_active = False
                auth_token.save()
                return JsonResponse({
                    'error': 'Token expirado',
                    'code': 'TOKEN_EXPIRED'
                }, status=401)
            
            # Decodificar token
            payload = decode_jwt_token(token)
            if not payload:
                return JsonResponse({
                    'error': 'Token inválido',
                    'code': 'TOKEN_INVALID'
                }, status=401)
            
            # Obtener usuario
            user = User.objects.get(id=payload['user_id'])
            request.user = user
            
        except AuthToken.DoesNotExist:
            return JsonResponse({
                'error': 'Token no válido',
                'code': 'TOKEN_NOT_FOUND'
            }, status=401)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'Usuario no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=401)
        
        return f(request, *args, **kwargs)
    
    return decorated_function

def premium_required(f):
    """Decorador que requiere membresía PREMIUM"""
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not hasattr(request, 'user'):
            return JsonResponse({
                'error': 'Usuario no autenticado',
                'code': 'USER_NOT_AUTHENTICATED'
            }, status=401)
        
        membership = MembershipHistory.get_current_membership(request.user)
        if membership != 'PREMIUM':
            return JsonResponse({
                'error': 'Necesitas membresía Premium para acceder a esta funcionalidad',
                'code': 'PREMIUM_REQUIRED',
                'current_membership': membership
            }, status=403)
        
        return f(request, *args, **kwargs)
    
    return decorated_function

def get_user_membership(user):
    """Obtiene la membresía actual del usuario"""
    return MembershipHistory.get_current_membership(user)
