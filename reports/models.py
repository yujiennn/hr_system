from django.db import models
from django.utils import timezone
from users.models import User


class ReportCategory(models.Model):
    """报表分类"""
    CATEGORY_CHOICES = [
        ('employee', '人事报表'),
        ('attendance', '考勤报表'),
        ('salary', '薪资报表'),
        ('performance', '绩效报表'),
        ('custom', '自定义报表'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='分类名称')
    code = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True, verbose_name='分类代码')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'report_category'
        verbose_name = '报表分类'
        verbose_name_plural = '报表分类'
    
    def __str__(self):
        return self.name


class ReportTemplate(models.Model):
    """报表模板"""
    FORMAT_CHOICES = [
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='模板名称')
    category = models.ForeignKey(ReportCategory, on_delete=models.CASCADE, verbose_name='分类')
    code = models.CharField(max_length=100, unique=True, verbose_name='模板代码')
    description = models.TextField(blank=True, verbose_name='描述')
    query_sql = models.TextField(blank=True, verbose_name='查询SQL')
    template_config = models.JSONField(default=dict, verbose_name='模板配置')
    default_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='xlsx', verbose_name='默认格式')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'report_template'
        verbose_name = '报表模板'
        verbose_name_plural = '报表模板'
    
    def __str__(self):
        return self.name


class Report(models.Model):
    """报表记录"""
    STATUS_CHOICES = [
        ('pending', '待生成'),
        ('processing', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='报表名称')
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='模板')
    parameters = models.JSONField(default=dict, verbose_name='报表参数')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='文件路径')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    file_format = models.CharField(max_length=10, verbose_name='文件格式')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='生成人')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'report'
        verbose_name = '报表'
        verbose_name_plural = '报表'
        ordering = ['-generated_at']
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """定时报表任务"""
    FREQUENCY_CHOICES = [
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
        ('quarterly', '每季度'),
        ('yearly', '每年'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='任务名称')
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='模板')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='频率')
    schedule_time = models.TimeField(verbose_name='执行时间')
    parameters = models.JSONField(default=dict, verbose_name='参数')
    formats = models.JSONField(default=list, verbose_name='输出格式')
    email_enabled = models.BooleanField(default=False, verbose_name='邮件通知')
    email_recipients = models.TextField(blank=True, verbose_name='收件人')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name='上次执行时间')
    next_run_at = models.DateTimeField(null=True, blank=True, verbose_name='下次执行时间')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'report_schedule'
        verbose_name = '定时报表任务'
        verbose_name_plural = '定时报表任务'
    
    def __str__(self):
        return self.name


class SystemLog(models.Model):
    """系统日志"""
    LEVEL_CHOICES = [
        ('debug', 'DEBUG'),
        ('info', 'INFO'),
        ('warning', 'WARNING'),
        ('error', 'ERROR'),
        ('critical', 'CRITICAL'),
    ]
    
    MODULE_CHOICES = [
        ('users', '用户管理'),
        ('attendance', '考勤管理'),
        ('salary', '薪资管理'),
        ('performance', '绩效管理'),
        ('leave', '请假管理'),
        ('reports', '报表管理'),
        ('system', '系统'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='时间')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='级别')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES, verbose_name='模块')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='用户')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    message = models.CharField(max_length=500, verbose_name='消息')
    full_message = models.TextField(blank=True, verbose_name='完整消息')
    stack_trace = models.TextField(blank=True, verbose_name='堆栈信息')
    session_id = models.CharField(max_length=100, blank=True, verbose_name='会话ID')
    request_id = models.CharField(max_length=100, blank=True, verbose_name='请求ID')
    file_name = models.CharField(max_length=200, blank=True, verbose_name='文件名')
    line_number = models.IntegerField(null=True, blank=True, verbose_name='行号')
    function_name = models.CharField(max_length=100, blank=True, verbose_name='函数名')
    
    class Meta:
        db_table = 'system_log'
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['module']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.message}"
