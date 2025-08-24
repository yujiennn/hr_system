from django.core.management.base import BaseCommand
from system_config.models import SystemConfig


class Command(BaseCommand):
    help = '初始化系统配置项'

    def handle(self, *args, **options):
        configs = [
            # 基础配置
            {'key': 'system_name', 'value': '智慧员工运营系统', 'config_type': 'basic', 'description': '系统名称'},
            {'key': 'company_name', 'value': '示例公司', 'config_type': 'basic', 'description': '公司名称'},
            {'key': 'system_version', 'value': '1.0.0', 'config_type': 'basic', 'description': '系统版本'},
            {'key': 'company_logo', 'value': '', 'config_type': 'basic', 'description': '公司Logo'},
            {'key': 'system_description', 'value': '智慧员工运营管理系统', 'config_type': 'basic', 'description': '系统描述'},
            {'key': 'contact_phone', 'value': '', 'config_type': 'basic', 'description': '联系电话'},
            {'key': 'system_url', 'value': 'http://localhost:8081', 'config_type': 'basic', 'description': '系统地址'},
            
            # 考勤配置
            {'key': 'work_start_time', 'value': '09:00', 'config_type': 'attendance', 'description': '上班时间'},
            {'key': 'work_end_time', 'value': '18:00', 'config_type': 'attendance', 'description': '下班时间'},
            {'key': 'lunch_start_time', 'value': '12:00', 'config_type': 'attendance', 'description': '午休开始时间'},
            {'key': 'lunch_end_time', 'value': '13:00', 'config_type': 'attendance', 'description': '午休结束时间'},
            {'key': 'late_threshold', 'value': '15', 'config_type': 'attendance', 'description': '迟到阈值(分钟)'},
            {'key': 'early_leave_threshold', 'value': '30', 'config_type': 'attendance', 'description': '早退阈值(分钟)'},
            {'key': 'work_days', 'value': '1,2,3,4,5', 'config_type': 'attendance', 'description': '工作日'},
            {'key': 'enable_location', 'value': 'true', 'config_type': 'attendance', 'description': '启用地理位置'},
            {'key': 'location_range', 'value': '200', 'config_type': 'attendance', 'description': '打卡范围(米)'},
            {'key': 'enable_face_recognition', 'value': 'false', 'config_type': 'attendance', 'description': '启用人脸识别'},
            
            # 通知配置
            {'key': 'notification_enabled', 'value': 'true', 'config_type': 'notification', 'description': '启用系统通知'},
            {'key': 'email_notification', 'value': 'true', 'config_type': 'notification', 'description': '启用邮件通知'},
            {'key': 'sms_notification', 'value': 'false', 'config_type': 'notification', 'description': '启用短信通知'},
            {'key': 'inapp_notification', 'value': 'true', 'config_type': 'notification', 'description': '启用站内通知'},
            {'key': 'attendance_alert', 'value': 'true', 'config_type': 'notification', 'description': '考勤异常通知'},
            {'key': 'leave_approval_alert', 'value': 'true', 'config_type': 'notification', 'description': '请假审批通知'},
            {'key': 'salary_alert', 'value': 'true', 'config_type': 'notification', 'description': '薪资发放通知'},
            {'key': 'birthday_reminder', 'value': 'true', 'config_type': 'notification', 'description': '生日提醒'},
            {'key': 'contract_expire_reminder', 'value': 'true', 'config_type': 'notification', 'description': '合同到期提醒'},
            {'key': 'reminder_days', 'value': '7', 'config_type': 'notification', 'description': '提醒提前天数'},
            
            # 系统维护配置
            {'key': 'maintenance_mode', 'value': 'false', 'config_type': 'maintenance', 'description': '维护模式'},
            {'key': 'maintenance_message', 'value': '系统正在维护中，请稍后再试', 'config_type': 'maintenance', 'description': '维护公告'},
            {'key': 'estimated_recovery_time', 'value': '', 'config_type': 'maintenance', 'description': '预计恢复时间'},
            {'key': 'data_retention_days', 'value': '365', 'config_type': 'maintenance', 'description': '数据保留天数'},
        ]

        created_count = 0
        updated_count = 0

        for config_data in configs:
            config, created = SystemConfig.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'创建配置: {config.key} = {config.value}')
            else:
                # 更新描述信息
                if config.description != config_data['description']:
                    config.description = config_data['description']
                    config.save()
                    updated_count += 1
                    self.stdout.write(f'更新配置: {config.key}')

        self.stdout.write(
            self.style.SUCCESS(
                f'配置初始化完成! 创建了 {created_count} 个新配置，更新了 {updated_count} 个配置。'
            )
        )
