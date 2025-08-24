from django.db import models
from django.utils import timezone
from users.models import User


class SalaryStructure(models.Model):
    """薪酬结构模型"""
    name = models.CharField(max_length=100, verbose_name='薪酬结构名称')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '薪酬结构'
        verbose_name_plural = '薪酬结构'

    def __str__(self):
        return self.name


class SalaryItem(models.Model):
    """薪酬项目模型"""
    ITEM_TYPE_CHOICES = [
        ('basic', '基本项目'),
        ('allowance', '津贴补助'),
        ('bonus', '奖金'),
        ('deduction', '扣除项目'),
    ]

    structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, verbose_name='薪酬结构')
    name = models.CharField(max_length=100, verbose_name='项目名称')
    code = models.CharField(max_length=20, verbose_name='项目编码')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, verbose_name='项目类型')
    is_taxable = models.BooleanField(default=True, verbose_name='是否计税')
    is_social_security = models.BooleanField(default=False, verbose_name='是否计入社保基数')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '薪酬项目'
        verbose_name_plural = '薪酬项目'
        ordering = ['order']

    def __str__(self):
        return f"{self.structure.name} - {self.name}"


class SalaryRecord(models.Model):
    """工资记录模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('approved', '已审批'),
        ('paid', '已发放'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='员工')
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    
    # 基本薪酬
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='基本工资')
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绩效奖金')
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='津贴补助')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加班费')
    
    # 扣除项目
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='社保扣除')
    housing_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='公积金扣除')
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='个人所得税')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='其他扣除')
    
    # 计算字段
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='应发工资')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='实发工资')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    pay_date = models.DateField(null=True, blank=True, verbose_name='发放日期')
    note = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '工资记录'
        verbose_name_plural = '工资记录'
        unique_together = ['user', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.user.username} - {self.year}年{self.month}月"

    def save(self, *args, **kwargs):
        # 计算应发和实发工资
        self.gross_salary = (self.basic_salary + self.performance_bonus + 
                           self.allowances + self.overtime_pay)
        self.net_salary = (self.gross_salary - self.social_security - 
                         self.housing_fund - self.income_tax - self.other_deductions)
        super().save(*args, **kwargs)


class SalaryDetail(models.Model):
    """工资明细模型"""
    salary_record = models.ForeignKey(SalaryRecord, on_delete=models.CASCADE, 
                                    related_name='details', verbose_name='工资记录')
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, verbose_name='薪酬项目')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    note = models.CharField(max_length=200, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '工资明细'
        verbose_name_plural = '工资明细'

    def __str__(self):
        return f"{self.salary_record} - {self.salary_item.name}"
