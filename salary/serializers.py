from rest_framework import serializers
from .models import SalaryRecord, SalaryStructure, SalaryItem, SalaryDetail, SalaryConfig


class SalaryConfigSerializer(serializers.ModelSerializer):
    """薪资配置序列化器"""
    class Meta:
        model = SalaryConfig
        fields = '__all__'


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__'


class SalaryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryItem
        fields = '__all__'


class SalaryDetailSerializer(serializers.ModelSerializer):
    salary_item_name = serializers.CharField(source='salary_item.name', read_only=True)
    
    class Meta:
        model = SalaryDetail
        fields = ['id', 'salary_item', 'salary_item_name', 'amount', 'note']


class SalaryRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='user.employee_id', read_only=True)
    department_name = serializers.CharField(source='user.department.name', read_only=True)
    details = SalaryDetailSerializer(many=True, read_only=True)
    
    # 绩效相关显示字段
    performance_level_display = serializers.CharField(source='get_performance_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # 绩效评估关联信息
    performance_period_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SalaryRecord
        fields = [
            'id', 'user', 'user_name', 'employee_id', 'department_name',
            'year', 'month', 'basic_salary', 'performance_bonus', 
            'allowances', 'overtime_pay', 
            # 绩效关联字段
            'performance_evaluation', 'performance_score', 'performance_level',
            'performance_level_display', 'performance_coefficient',
            # 全勤奖字段
            'full_attendance_bonus', 'is_full_attendance',
            # 考勤扣款字段
            'leave_deduction', 'late_deduction', 'absence_deduction',
            # 考勤统计字段
            'leave_days', 'sick_leave_days', 'personal_leave_days', 'other_leave_days',
            'late_count', 'early_leave_count', 'absence_count', 'actual_work_days',
            # 加班统计字段
            'overtime_hours', 'overtime_count',
            # 扣除项
            'social_security', 'housing_fund', 'income_tax', 'other_deductions',
            # 汇总
            'gross_salary', 'net_salary', 'status', 'status_display', 'pay_date',
            'performance_period_name',
            'note', 'created_at', 'updated_at', 'details'
        ]
        read_only_fields = ['gross_salary', 'net_salary', 'created_at', 'updated_at']
    
    def get_performance_period_name(self, obj):
        """获取绩效考核周期名称"""
        if obj.performance_evaluation and obj.performance_evaluation.goal:
            return obj.performance_evaluation.goal.period.name
        return None


class SalaryRecordCreateSerializer(serializers.ModelSerializer):
    """
    用于创建工资记录的序列化器
    
    财务部员工设置以下字段:
    - 基本工资 (basic_salary)
    - 津贴补助 (allowances)
    - 社保扣除 (social_security)
    - 公积金扣除 (housing_fund)
    - 个人所得税 (income_tax)
    - 其他扣除 (other_deductions)
    
    系统自动计算:
    - 绩效奖金 (performance_bonus) - 根据绩效评分和系数
    - 加班费 (overtime_pay) - 根据加班申请记录
    - 全勤奖 (full_attendance_bonus) - 根据考勤记录
    - 考勤扣款 (leave_deduction, late_deduction, absence_deduction)
    """
    auto_calculate = serializers.BooleanField(
        write_only=True, 
        default=True,  # 默认自动计算
        help_text='是否自动根据绩效和考勤计算绩效奖金、加班费、全勤奖'
    )
    
    class Meta:
        model = SalaryRecord
        fields = [
            # 财务设置的字段
            'user', 'year', 'month', 'basic_salary', 'allowances',
            'social_security', 'housing_fund', 'income_tax', 'other_deductions',
            'note', 'auto_calculate'
        ]
    
    def create(self, validated_data):
        auto_calculate = validated_data.pop('auto_calculate', True)
        # 创建时不设置需要自动计算的字段
        instance = SalaryRecord.objects.create(**validated_data)
        
        if auto_calculate:
            # 自动计算绩效奖金、加班费、全勤奖、考勤扣款
            instance.calculate_from_performance_and_attendance()
        
        return instance
    
    def update(self, instance, validated_data):
        auto_calculate = validated_data.pop('auto_calculate', True)
        
        # 更新财务设置的字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if auto_calculate:
            # 重新计算系统自动字段
            instance.calculate_from_performance_and_attendance()
        
        return instance
