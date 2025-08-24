from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class CompanyLocation(models.Model):
    """公司位置配置模型"""
    name = models.CharField(max_length=100, verbose_name='位置名称')
    address = models.CharField(max_length=255, verbose_name='详细地址')
    latitude = models.FloatField(verbose_name='纬度')
    longitude = models.FloatField(verbose_name='经度')
    radius = models.IntegerField(default=200, verbose_name='打卡范围(米)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(blank=True, verbose_name='位置描述')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '公司位置'
        verbose_name_plural = '公司位置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.address}"


class SystemConfig(models.Model):
    """系统配置模型"""
    CONFIG_TYPES = [
        ('basic', '基础配置'),
        ('attendance', '考勤配置'),
        ('email', '邮件配置'),
        ('security', '安全配置'),
        ('notification', '通知配置'),
        ('maintenance', '系统维护'),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    value = models.TextField(verbose_name='配置值')
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPES, verbose_name='配置类型')
    description = models.CharField(max_length=255, blank=True, verbose_name='配置描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='created_configs', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        
    def __str__(self):
        return f"{self.key}: {self.description}"
    
    def set_json_value(self, value):
        """设置JSON格式的配置值"""
        self.value = json.dumps(value, ensure_ascii=False)
    
    def get_json_value(self):
        """获取JSON格式的配置值"""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value
