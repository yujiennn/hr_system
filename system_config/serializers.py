from rest_framework import serializers
from .models import SystemConfig, CompanyLocation

class CompanyLocationSerializer(serializers.ModelSerializer):
    """公司位置序列化器"""
    
    class Meta:
        model = CompanyLocation
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'radius', 
                  'description', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    json_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'json_value', 'config_type', 'description', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_json_value(self, obj):
        return obj.get_json_value()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class SystemConfigUpdateSerializer(serializers.Serializer):
    """批量更新系统配置序列化器"""
    configs = serializers.ListField(
        child=serializers.DictField(),
        help_text="配置项列表"
    )

class EmailTestSerializer(serializers.Serializer):
    """邮件测试序列化器"""
    recipient = serializers.EmailField(help_text="收件人邮箱")
    subject = serializers.CharField(max_length=255, default="系统邮件测试")
    message = serializers.CharField(default="这是一封测试邮件，用于验证邮件配置是否正确。")

class SystemMaintenanceSerializer(serializers.Serializer):
    """系统维护序列化器"""
    action = serializers.ChoiceField(
        choices=['clear_logs', 'clear_cache', 'restart_system'],
        help_text="维护操作类型"
    )
    confirm = serializers.BooleanField(default=False, help_text="确认执行")
