from rest_framework import serializers
from .models import SalaryRecord, SalaryStructure, SalaryItem, SalaryDetail


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
    
    class Meta:
        model = SalaryRecord
        fields = [
            'id', 'user', 'user_name', 'employee_id', 'department_name',
            'year', 'month', 'basic_salary', 'performance_bonus', 
            'allowances', 'overtime_pay', 'social_security', 
            'housing_fund', 'income_tax', 'other_deductions',
            'gross_salary', 'net_salary', 'status', 'pay_date',
            'note', 'created_at', 'updated_at', 'details'
        ]
        read_only_fields = ['gross_salary', 'net_salary', 'created_at', 'updated_at']
