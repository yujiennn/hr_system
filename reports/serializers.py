from rest_framework import serializers
from .models import ReportCategory, ReportTemplate, Report, ReportSchedule, SystemLog


class ReportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCategory
        fields = '__all__'


class ReportTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'category', 'category_name', 'code', 'description',
            'query_sql', 'template_config', 'default_format', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'template', 'template_name', 'parameters',
            'file_path', 'file_size', 'file_size_display', 'file_format',
            'status', 'error_message', 'generated_by', 'generated_by_name',
            'generated_at', 'completed_at'
        ]
        read_only_fields = ['generated_by', 'generated_at', 'completed_at']
    
    def get_file_size_display(self, obj):
        """将文件大小转换为可读格式"""
        if obj.file_size == 0:
            return '0B'
        
        units = ['B', 'KB', 'MB', 'GB']
        size = float(obj.file_size)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f}{units[unit_index]}"


class ReportScheduleSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'name', 'template', 'template_name', 'frequency',
            'frequency_display', 'schedule_time', 'parameters', 'formats',
            'email_enabled', 'email_recipients', 'is_active',
            'last_run_at', 'next_run_at', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'last_run_at', 'next_run_at', 'created_at', 'updated_at']


class SystemLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    module_display = serializers.CharField(source='get_module_display', read_only=True)
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'timestamp', 'level', 'level_display', 'module',
            'module_display', 'user', 'user_name', 'ip_address',
            'user_agent', 'message', 'full_message', 'stack_trace',
            'session_id', 'request_id', 'file_name', 'line_number',
            'function_name'
        ]
        read_only_fields = ['timestamp']


class ReportGenerationSerializer(serializers.Serializer):
    """报表生成请求序列化器"""
    template_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    parameters = serializers.JSONField(default=dict)
    format = serializers.ChoiceField(
        choices=[('xlsx', 'Excel'), ('pdf', 'PDF'), ('csv', 'CSV'), ('json', 'JSON')],
        default='xlsx'
    )


class LogQuerySerializer(serializers.Serializer):
    """日志查询参数序列化器"""
    level = serializers.ChoiceField(
        choices=[('debug', 'DEBUG'), ('info', 'INFO'), ('warning', 'WARNING'), 
                ('error', 'ERROR'), ('critical', 'CRITICAL')],
        required=False
    )
    module = serializers.ChoiceField(
        choices=[('users', '用户管理'), ('attendance', '考勤管理'), ('salary', '薪资管理'),
                ('performance', '绩效管理'), ('leave', '请假管理'), ('reports', '报表管理'), ('system', '系统')],
        required=False
    )
    user_id = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    keyword = serializers.CharField(max_length=200, required=False)
    ip_address = serializers.IPAddressField(required=False)
