from django.contrib import admin
from .models import SalaryRecord, SalaryStructure, SalaryItem, SalaryDetail, SalaryConfig


@admin.register(SalaryConfig)
class SalaryConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'full_attendance_bonus', 'performance_bonus_base_rate', 
                   'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_active')
        }),
        ('全勤奖配置', {
            'fields': ('full_attendance_bonus',)
        }),
        ('绩效系数配置', {
            'fields': ('performance_level_a_min', 'performance_level_b_min', 'performance_level_c_min',
                      'performance_level_a_coefficient', 'performance_level_b_coefficient',
                      'performance_level_c_coefficient', 'performance_level_d_coefficient',
                      'performance_bonus_base_rate')
        }),
        ('请假扣款配置', {
            'fields': ('sick_leave_free_days', 'sick_leave_deduction_rate', 'personal_leave_deduction_rate')
        }),
        ('迟到扣款配置', {
            'fields': ('late_deduction_minor', 'late_deduction_major', 'late_threshold_minutes')
        }),
        ('其他配置', {
            'fields': ('absence_deduction_rate', 'work_days_per_month')
        }),
    )


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'basic_salary', 'performance_bonus', 
                   'full_attendance_bonus', 'gross_salary', 'net_salary', 'status']
    list_filter = ['status', 'year', 'month', 'is_full_attendance', 'performance_level']
    search_fields = ['user__username', 'user__employee_id']
    readonly_fields = ['gross_salary', 'net_salary', 'created_at', 'updated_at']


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(SalaryItem)
class SalaryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'structure', 'item_type', 'is_active', 'order']
    list_filter = ['structure', 'item_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(SalaryDetail)
class SalaryDetailAdmin(admin.ModelAdmin):
    list_display = ['salary_record', 'salary_item', 'amount']
    list_filter = ['salary_item']
