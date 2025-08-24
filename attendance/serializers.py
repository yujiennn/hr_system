from rest_framework import serializers
from .models import AttendanceRecord, WorkSchedule, AttendanceException
from users.serializers import UserSerializer


class AttendanceRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='user.employee_id', read_only=True)
    clock_type_display = serializers.CharField(source='get_clock_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'user', 'user_name', 'employee_id',
            'clock_time', 'clock_type', 'clock_type_display',
            'status', 'status_display', 'location',
            'latitude', 'longitude', 'face_image', 'note', 'created_at'
        ]
        read_only_fields = ['created_at']


class WorkScheduleSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'name', 'weekday', 'weekday_display',
            'start_time', 'end_time', 'late_threshold',
            'early_threshold', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class AttendanceExceptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='user.employee_id', read_only=True)
    exception_type_display = serializers.CharField(source='get_exception_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    
    class Meta:
        model = AttendanceException
        fields = [
            'id', 'user', 'user_name', 'employee_id',
            'exception_type', 'exception_type_display',
            'exception_date', 'reason', 'status', 'status_display',
            'approver', 'approver_name', 'approval_note',
            'approved_at', 'created_at'
        ]
        read_only_fields = ['approver', 'approved_at', 'created_at']
