from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import secrets

# Create your models here.

class User(AbstractUser):
    """Usuario personalizado con membresía"""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class MembershipHistory(models.Model):
    """Historial de membresías del usuario"""
    MEMBERSHIP_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_history')
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='FREE')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.membership_type}"
    
    @classmethod
    def get_current_membership(cls, user):
        """Obtiene la membresía actual del usuario"""
        current = cls.objects.filter(user=user, is_active=True).first()
        return current.membership_type if current else 'FREE'

class Document(models.Model):
    """Documentos importados desde Google Drive"""
    DOCUMENT_TYPES = [
        ('PDF', 'PDF Document'),
        ('EXCEL', 'Excel Spreadsheet'),
        ('GDOC', 'Google Document'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    google_drive_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    google_drive_url = models.URLField(blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.google_drive_id:
            # Generar un ID único si no se proporciona
            import uuid
            self.google_drive_id = f"local_{uuid.uuid4().hex[:16]}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-imported_at']
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"

class ExcelRow(models.Model):
    """Filas de datos extraídas de archivos Excel"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='excel_rows')
    row_number = models.IntegerField()
    data = models.JSONField()  # Almacena los datos de la fila como JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'row_number']
        unique_together = ['document', 'row_number']
    
    def __str__(self):
        return f"Row {self.row_number} of {self.document.title}"

class AuthToken(models.Model):
    """Tokens JWT para autenticación"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            from django.conf import settings
            self.expires_at = timezone.now() + timezone.timedelta(hours=getattr(settings, 'JWT_EXPIRATION_HOURS', 24))
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token for {self.user.email}"
