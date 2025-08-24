from django.contrib import admin
from .models import SystemConfig, CompanyLocation

@admin.register(CompanyLocation)
class CompanyLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'latitude', 'longitude', 'radius', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时设置创建者
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'config_type', 'description', 'is_active', 'created_at', 'updated_at']
    list_filter = ['config_type', 'is_active', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['config_type', 'key']
    
    def has_change_permission(self, request, obj=None):
        return False
