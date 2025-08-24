from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from system_config.models import SystemConfig

User = get_user_model()

class Command(BaseCommand):
    help = '初始化系统配置'

    def handle(self, *args, **options):
        # 获取超级用户
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
        except:
            admin_user = None

        # 默认系统配置
        default_configs = [
            # 基础配置
            {
                'key': 'system_name',
                'value': 'HR管理系统',
                'config_type': 'basic',
                'description': '系统名称'
            },
            {
                'key': 'system_version',
                'value': '1.0.0',
                'config_type': 'basic',
                'description': '系统版本'
            },
            {
                'key': 'company_name',
                'value': '示例公司',
                'config_type': 'basic',
                'description': '公司名称'
            },
            
            # 考勤配置
            {
                'key': 'work_start_time',
                'value': '09:00',
                'config_type': 'attendance',
                'description': '上班时间'
            },
            {
                'key': 'work_end_time',
                'value': '18:00',
                'config_type': 'attendance',
                'description': '下班时间'
            },
            {
                'key': 'lunch_start_time',
                'value': '12:00',
                'config_type': 'attendance',
                'description': '午休开始时间'
            },
            {
                'key': 'lunch_end_time',
                'value': '13:00',
                'config_type': 'attendance',
                'description': '午休结束时间'
            },
            
            # 邮件配置
            {
                'key': 'email_host',
                'value': 'smtp.gmail.com',
                'config_type': 'email',
                'description': 'SMTP服务器'
            },
            {
                'key': 'email_port',
                'value': '587',
                'config_type': 'email',
                'description': 'SMTP端口'
            },
            {
                'key': 'email_use_tls',
                'value': 'true',
                'config_type': 'email',
                'description': '启用TLS'
            },
            {
                'key': 'email_from',
                'value': 'hr@company.com',
                'config_type': 'email',
                'description': '发件人邮箱'
            },
            
            # 安全配置
            {
                'key': 'password_min_length',
                'value': '8',
                'config_type': 'security',
                'description': '密码最小长度'
            },
            {
                'key': 'login_max_attempts',
                'value': '5',
                'config_type': 'security',
                'description': '最大登录尝试次数'
            },
            {
                'key': 'session_timeout',
                'value': '3600',
                'config_type': 'security',
                'description': '会话超时时间(秒)'
            },
            
            # 通知配置
            {
                'key': 'notification_enabled',
                'value': 'true',
                'config_type': 'notification',
                'description': '启用通知'
            },
            {
                'key': 'email_notification',
                'value': 'true',
                'config_type': 'notification',
                'description': '邮件通知'
            },
            
            # 系统维护
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'config_type': 'maintenance',
                'description': '维护模式'
            },
            {
                'key': 'backup_enabled',
                'value': 'true',
                'config_type': 'maintenance',
                'description': '启用自动备份'
            }
        ]

        created_count = 0
        updated_count = 0

        for config_data in default_configs:
            config, created = SystemConfig.objects.get_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'config_type': config_data['config_type'],
                    'description': config_data['description'],
                    'created_by': admin_user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建配置: {config.key}')
                )
            else:
                # 更新描述信息
                if config.description != config_data['description']:
                    config.description = config_data['description']
                    config.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'更新配置: {config.key}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'系统配置初始化完成！创建 {created_count} 个新配置，更新 {updated_count} 个配置。'
            )
        )
