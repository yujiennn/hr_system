from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    is_finance_department = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'employee_id',
            'phone', 'user_type', 'department', 'department_name', 'avatar',
            'gender', 'birth_date', 'id_card', 'address', 'emergency_contact',
            'emergency_phone', 'hire_date', 'position', 'job_level', 'base_salary',
            'is_active_employee', 'created_at', 'updated_at', 'is_finance_department'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_finance_department']
    
    def get_is_finance_department(self, obj):
        """返回用户是否是财务部员工"""
        return obj.is_finance_department
    
    def to_representation(self, instance):
        """序列化时返回完整的avatar URL"""
        ret = super().to_representation(instance)
        if instance.avatar:
            request = self.context.get('request')
            if request:
                ret['avatar'] = request.build_absolute_uri(instance.avatar.url)
            else:
                ret['avatar'] = f"http://127.0.0.1:8000{instance.avatar.url}"
        return ret


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    hire_date = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password', 'first_name',
            'last_name', 'employee_id', 'phone', 'user_type', 'department',
            'gender', 'birth_date', 'id_card', 'address', 'emergency_contact',
            'emergency_phone', 'hire_date', 'position', 'job_level', 'base_salary'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("密码不匹配")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账号已被禁用')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("新密码不匹配")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码错误")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    is_finance_department = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'employee_id',
            'phone', 'user_type', 'department', 'department_name', 'avatar',
            'gender', 'birth_date', 'id_card', 'address', 'emergency_contact',
            'emergency_phone', 'position', 'job_level', 'hire_date',
            'education', 'major', 'university', 'work_experience', 'skills', 'bio',
            'is_finance_department'
        ]
        read_only_fields = ['id', 'username', 'employee_id', 'user_type', 'department', 'is_finance_department']
    
    def get_is_finance_department(self, obj):
        """返回用户是否是财务部员工"""
        return obj.is_finance_department
    
    def to_representation(self, instance):
        """序列化时返回完整的avatar URL"""
        ret = super().to_representation(instance)
        if instance.avatar:
            request = self.context.get('request')
            if request:
                ret['avatar'] = request.build_absolute_uri(instance.avatar.url)
            else:
                ret['avatar'] = f"http://127.0.0.1:8000{instance.avatar.url}"
        return ret
