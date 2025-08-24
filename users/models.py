from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def get_current_date():
    """获取当前日期"""
    return timezone.now().date()


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    description = models.TextField(blank=True, verbose_name='部门描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='上级部门')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户模型"""
    USER_TYPE_CHOICES = [
        ('employee', '普通员工'),
        ('manager', '部门经理'),
        ('admin', '系统管理员'),
    ]
    
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, verbose_name='员工编号')
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号码')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee', verbose_name='用户类型')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属部门')
      # 个人信息
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='性别')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    id_card = models.CharField(max_length=18, unique=True, null=True, blank=True, verbose_name='身份证号')
    address = models.CharField(max_length=200, blank=True, verbose_name='家庭住址')
    emergency_contact = models.CharField(max_length=50, blank=True, verbose_name='紧急联系人')
    emergency_phone = models.CharField(max_length=11, blank=True, verbose_name='紧急联系人电话')
    
    # 人脸识别相关字段
    face_encoding = models.TextField(blank=True, null=True, verbose_name='人脸特征编码')
    face_image = models.ImageField(upload_to='face_images/', null=True, blank=True, verbose_name='人脸图片')
    face_registered = models.BooleanField(default=False, verbose_name='是否已录入人脸')
    face_registered_at = models.DateTimeField(null=True, blank=True, verbose_name='人脸录入时间')
    emergency_phone = models.CharField(max_length=11, blank=True, verbose_name='紧急联系人电话')
    
    # 教育背景和技能
    education = models.CharField(max_length=50, blank=True, verbose_name='教育程度')
    major = models.CharField(max_length=100, blank=True, verbose_name='专业')
    university = models.CharField(max_length=100, blank=True, verbose_name='毕业院校')
    work_experience = models.TextField(blank=True, verbose_name='工作经验')
    skills = models.TextField(blank=True, verbose_name='专业技能')
    bio = models.TextField(blank=True, verbose_name='个人简介')# 工作信息
    hire_date = models.DateField(default=get_current_date, verbose_name='入职日期')
    position = models.CharField(max_length=100, blank=True, verbose_name='职位')
    job_level = models.CharField(max_length=50, blank=True, verbose_name='职级')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='基本工资')
    
    # 系统信息
    is_active_employee = models.BooleanField(default=True, verbose_name='是否在职')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name() or self.username}"

    @property
    def is_manager(self):
        return self.user_type == 'manager'

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_employee(self):
        return self.user_type == 'employee'
