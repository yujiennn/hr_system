from django.db import models
from django.utils import timezone
from users.models import User


class PerformancePeriod(models.Model):
    """绩效考核周期模型"""
    PERIOD_TYPE_CHOICES = [
        ('monthly', '月度'),
        ('quarterly', '季度'),
        ('yearly', '年度'),
    ]

    name = models.CharField(max_length=100, verbose_name='周期名称')
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES, verbose_name='周期类型')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '绩效考核周期'
        verbose_name_plural = '绩效考核周期'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class PerformanceTemplate(models.Model):
    """绩效模板模型"""
    name = models.CharField(max_length=100, verbose_name='模板名称')
    description = models.TextField(blank=True, verbose_name='描述')
    total_score = models.IntegerField(default=100, verbose_name='总分')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '绩效模板'
        verbose_name_plural = '绩效模板'

    def __str__(self):
        return self.name


class PerformanceIndicator(models.Model):
    """绩效指标模型"""
    template = models.ForeignKey(PerformanceTemplate, on_delete=models.CASCADE, 
                               related_name='indicators', verbose_name='绩效模板')
    name = models.CharField(max_length=100, verbose_name='指标名称')
    description = models.TextField(blank=True, verbose_name='指标描述')
    weight = models.FloatField(verbose_name='权重(%)')
    max_score = models.IntegerField(default=100, verbose_name='满分')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '绩效指标'
        verbose_name_plural = '绩效指标'
        ordering = ['order']

    def __str__(self):
        return f"{self.template.name} - {self.name}"


class PerformanceGoal(models.Model):
    """绩效目标模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='员工')
    period = models.ForeignKey(PerformancePeriod, on_delete=models.CASCADE, verbose_name='考核周期')
    template = models.ForeignKey(PerformanceTemplate, on_delete=models.CASCADE, verbose_name='绩效模板')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    # 审批信息
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='approved_goals', verbose_name='审批人')
    approval_note = models.TextField(blank=True, verbose_name='审批意见')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效目标'
        verbose_name_plural = '绩效目标'
        unique_together = ['user', 'period']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.period.name}"


class PerformanceGoalDetail(models.Model):
    """绩效目标明细模型"""
    goal = models.ForeignKey(PerformanceGoal, on_delete=models.CASCADE, 
                           related_name='details', verbose_name='绩效目标')
    indicator = models.ForeignKey(PerformanceIndicator, on_delete=models.CASCADE, verbose_name='绩效指标')
    target_value = models.TextField(verbose_name='目标值')
    weight = models.FloatField(verbose_name='权重(%)')

    class Meta:
        verbose_name = '绩效目标明细'
        verbose_name_plural = '绩效目标明细'

    def __str__(self):
        return f"{self.goal} - {self.indicator.name}"


class PerformanceEvaluation(models.Model):
    """绩效评估模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('self_evaluated', '自评完成'),
        ('manager_evaluated', '上级评估完成'),
        ('finalized', '已完成'),
    ]

    RATING_CHOICES = [
        ('excellent', '优秀'),
        ('good', '良好'),
        ('average', '一般'),
        ('poor', '差'),
    ]

    goal = models.OneToOneField(PerformanceGoal, on_delete=models.CASCADE, verbose_name='绩效目标')
    
    # 自评
    self_evaluation_score = models.FloatField(null=True, blank=True, verbose_name='自评分数')
    self_evaluation_comment = models.TextField(blank=True, verbose_name='自评意见')
    self_evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name='自评时间')
    
    # 上级评估
    manager_evaluation_score = models.FloatField(null=True, blank=True, verbose_name='上级评分')
    manager_evaluation_comment = models.TextField(blank=True, verbose_name='上级评估意见')
    manager_evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name='上级评估时间')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='evaluations', verbose_name='评估人')
    
    # 最终结果
    final_score = models.FloatField(null=True, blank=True, verbose_name='最终得分')
    final_rating = models.CharField(max_length=10, choices=RATING_CHOICES, null=True, blank=True, verbose_name='最终等级')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效评估'
        verbose_name_plural = '绩效评估'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.goal.user.username} - {self.goal.period.name}"


class PerformanceEvaluationDetail(models.Model):
    """绩效评估明细模型"""
    evaluation = models.ForeignKey(PerformanceEvaluation, on_delete=models.CASCADE,
                                 related_name='details', verbose_name='绩效评估')
    indicator = models.ForeignKey(PerformanceIndicator, on_delete=models.CASCADE, verbose_name='绩效指标')
    
    # 自评
    self_score = models.FloatField(null=True, blank=True, verbose_name='自评分数')
    self_comment = models.TextField(blank=True, verbose_name='自评说明')
    
    # 上级评分
    manager_score = models.FloatField(null=True, blank=True, verbose_name='上级评分')
    manager_comment = models.TextField(blank=True, verbose_name='上级评价')
    
    # 最终分数
    final_score = models.FloatField(null=True, blank=True, verbose_name='最终分数')

    class Meta:
        verbose_name = '绩效评估明细'
        verbose_name_plural = '绩效评估明细'

    def __str__(self):
        return f"{self.evaluation} - {self.indicator.name}"
