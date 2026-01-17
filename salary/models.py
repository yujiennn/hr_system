from django.db import models
from django.utils import timezone
from decimal import Decimal
from users.models import User


class SalaryConfig(models.Model):
    """薪资计算配置模型"""
    name = models.CharField(max_length=100, verbose_name='配置名称')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 全勤奖配置
    full_attendance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=500, 
                                                verbose_name='全勤奖金额')
    
    # 绩效系数配置
    performance_level_a_min = models.FloatField(default=90, verbose_name='A级最低分')
    performance_level_b_min = models.FloatField(default=80, verbose_name='B级最低分')
    performance_level_c_min = models.FloatField(default=60, verbose_name='C级最低分')
    
    performance_level_a_coefficient = models.FloatField(default=1.5, verbose_name='A级绩效系数')
    performance_level_b_coefficient = models.FloatField(default=1.2, verbose_name='B级绩效系数')
    performance_level_c_coefficient = models.FloatField(default=1.0, verbose_name='C级绩效系数')
    performance_level_d_coefficient = models.FloatField(default=0.5, verbose_name='D级绩效系数')
    
    performance_bonus_base_rate = models.FloatField(default=0.2, verbose_name='绩效奖金基数比例')
    
    # 加班费配置
    overtime_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=50, 
                                               verbose_name='加班时薪(元/小时)')
    overtime_weekend_rate = models.FloatField(default=1.5, verbose_name='周末加班系数')
    overtime_holiday_rate = models.FloatField(default=2.0, verbose_name='节假日加班系数')
    
    # 请假扣款配置
    sick_leave_free_days = models.IntegerField(default=2, verbose_name='病假免扣天数')
    sick_leave_deduction_rate = models.FloatField(default=0.5, verbose_name='病假扣款比例')
    personal_leave_deduction_rate = models.FloatField(default=1.0, verbose_name='事假扣款比例')
    
    # 迟到扣款配置
    late_deduction_minor = models.DecimalField(max_digits=10, decimal_places=2, default=20, 
                                               verbose_name='轻微迟到扣款')
    late_deduction_major = models.DecimalField(max_digits=10, decimal_places=2, default=50, 
                                               verbose_name='严重迟到扣款')
    late_threshold_minutes = models.IntegerField(default=30, verbose_name='迟到严重阈值(分钟)')
    
    # 缺勤扣款配置
    absence_deduction_rate = models.FloatField(default=1.0, verbose_name='缺勤扣款比例(按日薪)')
    
    # 工作日配置
    work_days_per_month = models.IntegerField(default=22, verbose_name='每月工作日')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '薪资计算配置'
        verbose_name_plural = '薪资计算配置'
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_active_config(cls):
        """获取当前启用的配置"""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            # 如果没有配置，创建默认配置
            config = cls.objects.create(name='默认配置', is_active=True)
        return config
    
    def get_performance_level(self, score):
        """根据绩效得分获取等级"""
        if score >= self.performance_level_a_min:
            return 'A'
        elif score >= self.performance_level_b_min:
            return 'B'
        elif score >= self.performance_level_c_min:
            return 'C'
        else:
            return 'D'
    
    def get_performance_coefficient(self, level):
        """根据绩效等级获取系数"""
        coefficients = {
            'A': self.performance_level_a_coefficient,
            'B': self.performance_level_b_coefficient,
            'C': self.performance_level_c_coefficient,
            'D': self.performance_level_d_coefficient,
        }
        return coefficients.get(level, 1.0)


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
        ('manager_reviewed', '经理已审核'),
        ('finance_approved', '财务已批准'),
        ('paid', '已发放'),
        ('rejected', '已拒绝'),
    ]
    
    PERFORMANCE_LEVEL_CHOICES = [
        ('A', '优秀'),
        ('B', '良好'),
        ('C', '合格'),
        ('D', '待改进'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='员工')
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    
    # 基本薪酬
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='基本工资')
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绩效奖金')
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='津贴补助')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加班费')
    
    # === 绩效关联字段 ===
    performance_evaluation = models.ForeignKey('performance.PerformanceEvaluation', 
                                               on_delete=models.SET_NULL, null=True, blank=True,
                                               verbose_name='绩效评估')
    performance_score = models.FloatField(null=True, blank=True, verbose_name='绩效得分')
    performance_level = models.CharField(max_length=1, choices=PERFORMANCE_LEVEL_CHOICES, 
                                         null=True, blank=True, verbose_name='绩效等级')
    performance_coefficient = models.FloatField(default=1.0, verbose_name='绩效系数')
    
    # === 全勤奖相关 ===
    full_attendance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                                verbose_name='全勤奖')
    is_full_attendance = models.BooleanField(default=False, verbose_name='是否全勤')
    
    # === 考勤与请假扣款 ===
    leave_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                          verbose_name='请假扣款')
    late_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                         verbose_name='迟到扣款')
    absence_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                            verbose_name='缺勤扣款')
    
    # === 考勤统计字段 ===
    leave_days = models.FloatField(default=0, verbose_name='当月请假天数')
    sick_leave_days = models.FloatField(default=0, verbose_name='病假天数')
    personal_leave_days = models.FloatField(default=0, verbose_name='事假天数')
    other_leave_days = models.FloatField(default=0, verbose_name='其他假期天数')
    late_count = models.IntegerField(default=0, verbose_name='迟到次数')
    early_leave_count = models.IntegerField(default=0, verbose_name='早退次数')
    absence_count = models.IntegerField(default=0, verbose_name='缺勤次数')
    actual_work_days = models.IntegerField(default=0, verbose_name='实际出勤天数')
    
    # === 加班统计字段 ===
    overtime_hours = models.FloatField(default=0, verbose_name='加班小时数')
    overtime_count = models.IntegerField(default=0, verbose_name='加班次数')
    
    # 扣除项目
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='社保扣除')
    housing_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='公积金扣除')
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='个人所得税')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='其他扣除')
    
    # 计算字段
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='应发工资')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='实发工资')
    
    # 审批信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    # 经理审核
    manager_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='经理审核时间')
    manager_note = models.TextField(blank=True, verbose_name='经理审核意见')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='reviewed_salaries', verbose_name='审核经理')
    
    # 财务批准
    finance_approved_at = models.DateTimeField(null=True, blank=True, verbose_name='财务批准时间')
    finance_note = models.TextField(blank=True, verbose_name='财务批准意见')
    finance_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='approved_salaries', verbose_name='财务批准人')
    
    # 发放信息
    pay_date = models.DateField(null=True, blank=True, verbose_name='发放日期')
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='paid_salaries', verbose_name='发放人')
    
    # 拒绝信息（如果状态为rejected）
    rejection_reason = models.TextField(blank=True, verbose_name='拒绝原因')
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name='拒绝时间')
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='rejected_salaries', verbose_name='拒绝人')
    
    note = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '工资记录'
        verbose_name_plural = '工资记录'
        unique_together = ['user', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.user.username} - {self.year}年{self.month}月"

    def save(self, *args, **kwargs):
        # 计算应发工资（包含全勤奖）
        self.gross_salary = (self.basic_salary + self.performance_bonus + 
                           self.allowances + self.overtime_pay + self.full_attendance_bonus)
        # 计算实发工资（扣除各项）
        total_deductions = (self.social_security + self.housing_fund + self.income_tax + 
                          self.other_deductions + self.leave_deduction + 
                          self.late_deduction + self.absence_deduction)
        self.net_salary = self.gross_salary - total_deductions
        super().save(*args, **kwargs)
    
    def calculate_from_performance_and_attendance(self, config=None):
        """
        根据绩效和考勤数据自动计算工资各项
        此方法由视图层调用，用于自动生成工资单
        财务只需设置: 基本工资、津贴、社保、公积金、个税、其他扣除
        系统自动计算: 绩效奖金、加班费、全勤奖、考勤扣款
        """
        from attendance.models import AttendanceRecord, AttendanceException
        from leave.models import LeaveApplication, LeaveType
        from performance.models import PerformanceEvaluation, PerformancePeriod
        from datetime import date
        import calendar
        
        if config is None:
            config = SalaryConfig.get_active_config()
        
        # 计算当月日薪
        daily_salary = self.basic_salary / Decimal(str(config.work_days_per_month))
        
        # === 1. 获取绩效评估数据，自动计算绩效奖金 ===
        try:
            period = PerformancePeriod.objects.filter(
                start_date__year=self.year,
                start_date__month__lte=self.month,
                end_date__month__gte=self.month,
                is_active=True
            ).first()
            
            if period:
                evaluation = PerformanceEvaluation.objects.filter(
                    goal__user=self.user,
                    goal__period=period,
                    status='finalized'  # 只取已完成的评估
                ).first()
                
                if evaluation and evaluation.final_score is not None:
                    self.performance_evaluation = evaluation
                    self.performance_score = evaluation.final_score
                    self.performance_level = config.get_performance_level(evaluation.final_score)
                    self.performance_coefficient = config.get_performance_coefficient(self.performance_level)
                    
                    # 自动计算绩效奖金 = 基本工资 × 基数比例 × 绩效系数
                    base_bonus = self.basic_salary * Decimal(str(config.performance_bonus_base_rate))
                    self.performance_bonus = base_bonus * Decimal(str(self.performance_coefficient))
        except Exception:
            pass  # 如果没有绩效数据，保持默认值
        
        # === 2. 统计考勤数据 ===
        month_start = date(self.year, self.month, 1)
        _, last_day = calendar.monthrange(self.year, self.month)
        month_end = date(self.year, self.month, last_day)
        
        # 获取当月考勤记录
        attendance_records = AttendanceRecord.objects.filter(
            user=self.user,
            clock_time__date__gte=month_start,
            clock_time__date__lte=month_end
        )
        
        # 统计迟到、早退、缺勤
        self.late_count = attendance_records.filter(status='late').count()
        self.early_leave_count = attendance_records.filter(status='early').count()
        self.absence_count = attendance_records.filter(status='absent').count()
        
        # 计算迟到扣款
        self.late_deduction = Decimal(str(self.late_count)) * config.late_deduction_minor
        
        # 计算缺勤扣款
        self.absence_deduction = Decimal(str(self.absence_count)) * daily_salary * Decimal(str(config.absence_deduction_rate))
        
        # === 3. 统计加班数据，自动计算加班费 ===
        overtime_applications = AttendanceException.objects.filter(
            user=self.user,
            exception_type='overtime',
            status='approved',
            exception_date__gte=month_start,
            exception_date__lte=month_end
        )
        
        self.overtime_count = overtime_applications.count()
        total_overtime_hours = sum(
            ot.overtime_hours or 0 for ot in overtime_applications
        )
        self.overtime_hours = total_overtime_hours
        
        # 自动计算加班费 = 加班小时数 × 时薪
        self.overtime_pay = Decimal(str(total_overtime_hours)) * config.overtime_hourly_rate
        
        # === 4. 统计请假数据 ===
        leave_applications = LeaveApplication.objects.filter(
            user=self.user,
            status='approved',
            start_date__lte=month_end,
            end_date__gte=month_start
        )
        
        self.sick_leave_days = 0
        self.personal_leave_days = 0
        self.other_leave_days = 0
        
        for leave in leave_applications:
            # 计算当月内的请假天数
            leave_start = max(leave.start_date, month_start)
            leave_end = min(leave.end_date, month_end)
            days_in_month = (leave_end - leave_start).days + 1
            
            if leave.leave_type.name in ['病假', '病假(带薪)']:
                self.sick_leave_days += days_in_month
            elif leave.leave_type.name in ['事假', '事假(不带薪)']:
                self.personal_leave_days += days_in_month
            else:
                self.other_leave_days += days_in_month
        
        self.leave_days = self.sick_leave_days + self.personal_leave_days + self.other_leave_days
        
        # 计算请假扣款
        # 病假：超过免扣天数的部分按比例扣
        sick_deductible_days = max(0, self.sick_leave_days - config.sick_leave_free_days)
        sick_deduction = Decimal(str(sick_deductible_days)) * daily_salary * Decimal(str(config.sick_leave_deduction_rate))
        
        # 事假：全额扣
        personal_deduction = Decimal(str(self.personal_leave_days)) * daily_salary * Decimal(str(config.personal_leave_deduction_rate))
        
        self.leave_deduction = sick_deduction + personal_deduction
        
        # === 5. 计算全勤奖 ===
        # 全勤条件：无请假（带薪假除外）、无迟到、无早退、无缺勤
        has_unpaid_leave = self.personal_leave_days > 0 or self.sick_leave_days > config.sick_leave_free_days
        has_attendance_issue = self.late_count > 0 or self.early_leave_count > 0 or self.absence_count > 0
        
        if not has_unpaid_leave and not has_attendance_issue:
            self.is_full_attendance = True
            self.full_attendance_bonus = config.full_attendance_bonus
        else:
            self.is_full_attendance = False
            self.full_attendance_bonus = Decimal('0')
        
        # 保存计算结果
        self.save()


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
