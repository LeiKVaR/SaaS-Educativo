import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from .models import User, MembershipHistory
from .utils import generate_jwt_token, jwt_required, get_user_membership


# ---------- Renderizado de páginas ----------

def home(request):
    return render(request, "home.html")

def login_view(request):
    return render(request, "Login.html")

def register_view(request):
    return render(request, "Register.html")


# ---------- API JSON ----------
@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    """Registro de nuevos usuarios (API)"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        username = data.get('username', email.split('@')[0])
        
        if not email or not password:
            return JsonResponse({
                'error': 'Email y contraseña son requeridos',
                'code': 'MISSING_FIELDS'
            }, status=400)
        
        # Verificar si el usuario ya existe
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'error': 'El usuario ya existe',
                'code': 'USER_EXISTS'
            }, status=400)
        
        # Crear usuario
        user = User.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        
        # Membresía FREE por defecto
        MembershipHistory.objects.create(
            user=user,
            membership_type='FREE'
        )
        
        # Generar token JWT
        token = generate_jwt_token(user)
        
        return JsonResponse({
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'membership': 'FREE'
            },
            'token': token
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


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """Inicio de sesión de usuarios (API)"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({
                'error': 'Email y contraseña son requeridos',
                'code': 'MISSING_FIELDS'
            }, status=400)
        
        # Buscar usuario
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'Credenciales inválidas',
                'code': 'INVALID_CREDENTIALS'
            }, status=401)
        
        # Verificar contraseña
        if not user.check_password(password):
            return JsonResponse({
                'error': 'Credenciales inválidas',
                'code': 'INVALID_CREDENTIALS'
            }, status=401)
        
        # Generar token
        token = generate_jwt_token(user)
        membership = get_user_membership(user)
        
        return JsonResponse({
            'message': 'Inicio de sesión exitoso',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'membership': membership
            },
            'token': token
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


@jwt_required
@require_http_methods(["GET"])
def profile(request):
    """Obtener perfil del usuario autenticado"""
    try:
        user = request.user
        membership = get_user_membership(user)
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'membership': membership,
                'created_at': user.created_at.isoformat(),
                'documents_count': user.documents.count()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=500)
