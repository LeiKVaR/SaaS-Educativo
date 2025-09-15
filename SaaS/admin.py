from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, MembershipHistory, Document, ExcelRow, AuthToken

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_active', 'created_at', 'get_current_membership')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_current_membership(self, obj):
        return MembershipHistory.get_current_membership(obj)
    get_current_membership.short_description = 'Membresía Actual'


@admin.register(MembershipHistory)
class MembershipHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'started_at', 'ended_at', 'is_active')
    list_filter = ('membership_type', 'is_active', 'started_at')
    search_fields = ('user__email', 'user__username')
    ordering = ('-started_at',)
    readonly_fields = ('started_at',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'document_type', 'is_processed', 'imported_at')
    list_filter = ('document_type', 'is_processed', 'imported_at')
    search_fields = ('title', 'user__email', 'google_drive_id')
    ordering = ('-imported_at',)
    readonly_fields = ('imported_at', 'google_drive_id')

    # 🔐 Restringir documentos visibles
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(ExcelRow)
class ExcelRowAdmin(admin.ModelAdmin):
    list_display = ('document', 'row_number', 'created_at')
    list_filter = ('document__document_type', 'created_at')
    search_fields = ('document__title', 'document__user__email')
    ordering = ('document', 'row_number')
    readonly_fields = ('created_at',)

    # 🔐 Restringir filas a documentos del usuario
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(document__user=request.user)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_active', 'is_expired_display')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'expires_at')
    
    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expirado'
