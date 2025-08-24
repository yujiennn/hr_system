from rest_framework import serializers
from .models import LeaveType, LeaveApplication, LeaveBalance


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveApplicationSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'user', 'user_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'days', 'reason', 'status',
            'approver', 'approver_name', 'approval_note', 'approved_at',
            'attachment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'days', 'approver', 'approval_note', 'approved_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """验证请假申请数据"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError("结束日期不能早于开始日期")
            
            # 检查日期不能是过去的日期
            from datetime import date
            if start_date < date.today():
                raise serializers.ValidationError("开始日期不能是过去的日期")
        
        return data
    
    def validate_reason(self, value):
        """验证请假原因"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("请假原因至少需要10个字符")
        return value
    
    def get_user_name(self, obj):
        if obj.user:
            if obj.user.first_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.username
        return ""
    
    def get_approver_name(self, obj):
        if obj.approver:
            if obj.approver.first_name:
                return f"{obj.approver.first_name} {obj.approver.last_name}"
            return obj.approver.username
        return ""


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'user', 'user_name', 'leave_type', 'leave_type_name',
            'year', 'total_days', 'used_days', 'remaining_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'remaining_days', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        if obj.user:
            if obj.user.first_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.username
        return ""


class LeaveApprovalSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    approval_note = serializers.CharField(required=False, allow_blank=True)
