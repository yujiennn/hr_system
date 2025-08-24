from django.db import models
from django.utils import timezone
from users.models import User


class AttendanceRecord(models.Model):
    """考勤记录模型"""
    CLOCK_TYPE_CHOICES = [
        ('in', '上班打卡'),
        ('out', '下班打卡'),
    ]
    
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('late', '迟到'),
        ('early', '早退'),
        ('absent', '缺勤'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='员工')
    clock_time = models.DateTimeField(verbose_name='打卡时间')
    clock_type = models.CharField(max_length=3, choices=CLOCK_TYPE_CHOICES, verbose_name='打卡类型')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal', verbose_name='状态')
    location = models.CharField(max_length=200, blank=True, verbose_name='打卡位置')
    latitude = models.FloatField(null=True, blank=True, verbose_name='纬度')
    longitude = models.FloatField(null=True, blank=True, verbose_name='经度')
    face_image = models.ImageField(upload_to='face_images/', null=True, blank=True, verbose_name='人脸照片')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录'
        ordering = ['-clock_time']

    def __str__(self):
        return f"{self.user.username} - {self.get_clock_type_display()} - {self.clock_time}"


class WorkSchedule(models.Model):
    """工作时间表模型"""
    WEEKDAY_CHOICES = [
        (1, '周一'),
        (2, '周二'),
        (3, '周三'),
        (4, '周四'),
        (5, '周五'),
        (6, '周六'),
        (7, '周日'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='班次名称')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name='星期')
    start_time = models.TimeField(verbose_name='上班时间')
    end_time = models.TimeField(verbose_name='下班时间')
    late_threshold = models.IntegerField(default=10, verbose_name='迟到阈值(分钟)')
    early_threshold = models.IntegerField(default=10, verbose_name='早退阈值(分钟)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '工作时间表'
        verbose_name_plural = '工作时间表'

    def __str__(self):
        return f"{self.name} - {self.get_weekday_display()}"


class AttendanceException(models.Model):
    """考勤异常申请模型"""
    EXCEPTION_TYPE_CHOICES = [
        ('late', '迟到申请'),
        ('early', '早退申请'),
        ('absent', '缺勤申请'),
        ('overtime', '加班申请'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    exception_type = models.CharField(max_length=10, choices=EXCEPTION_TYPE_CHOICES, verbose_name='异常类型')
    exception_date = models.DateField(verbose_name='异常日期')
    reason = models.TextField(verbose_name='申请原因')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='审批状态')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='approved_exceptions', verbose_name='审批人')
    approval_note = models.TextField(blank=True, verbose_name='审批意见')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '考勤异常申请'
        verbose_name_plural = '考勤异常申请'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_exception_type_display()}"
