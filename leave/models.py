from django.db import models
from django.utils import timezone
from users.models import User


class LeaveType(models.Model):
    """请假类型模型"""
    name = models.CharField(max_length=50, verbose_name='请假类型')
    description = models.TextField(blank=True, verbose_name='描述')
    max_days_per_year = models.IntegerField(default=0, verbose_name='每年最大天数')
    is_paid = models.BooleanField(default=True, verbose_name='是否带薪')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '请假类型'
        verbose_name_plural = '请假类型'

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    """请假申请模型"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='请假类型')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    days = models.FloatField(verbose_name='请假天数')
    reason = models.TextField(verbose_name='请假原因')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 审批信息
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='approved_leaves', verbose_name='审批人')
    approval_note = models.TextField(blank=True, verbose_name='审批意见')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    
    # 附件
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True, verbose_name='附件')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = '请假申请'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} - {self.start_date}"

    def save(self, *args, **kwargs):
        # 计算请假天数
        if self.start_date and self.end_date:
            self.days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)


class LeaveBalance(models.Model):
    """请假余额模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='员工')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='请假类型')
    year = models.IntegerField(verbose_name='年份')
    total_days = models.FloatField(default=0, verbose_name='总天数')
    used_days = models.FloatField(default=0, verbose_name='已用天数')
    remaining_days = models.FloatField(default=0, verbose_name='剩余天数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '请假余额'
        verbose_name_plural = '请假余额'
        unique_together = ['user', 'leave_type', 'year']

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} - {self.year}"

    def save(self, *args, **kwargs):
        self.remaining_days = self.total_days - self.used_days
        super().save(*args, **kwargs)
