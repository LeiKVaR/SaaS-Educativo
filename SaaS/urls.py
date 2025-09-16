from django.urls import path
from . import views, drive_views, admin_views

urlpatterns = [
    # Páginas HTML
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_page'),

    # Autenticación (API JSON)
    path('api/auth/register', views.register_api, name='register_api'),
    path('api/auth/login', views.login_api, name='login_api'),
    path('api/auth/profile', views.profile, name='profile'),
    
    # Google Drive
    path('api/drive/create-doc', drive_views.create_document, name='create_document'),
    path('api/drive/list-files', drive_views.list_files, name='list_files'),
    path('api/drive/list-google-files', drive_views.list_google_drive_files, name='list_google_drive_files'),
    path('api/drive/import-file/<str:file_id>', drive_views.import_file, name='import_file'),
    
    # Documentos
    path('api/documents', drive_views.list_user_documents, name='list_user_documents'),
    path('api/documents/<int:document_id>/rows', drive_views.get_document_rows, name='get_document_rows'),
    
    # Administración
    path('api/admin/users', admin_views.list_users, name='list_users'),
    path('api/admin/users/<int:user_id>/membership', admin_views.change_membership, name='change_membership'),
]
