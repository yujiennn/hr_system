from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.models import ReportCategory, ReportTemplate, SystemLog
from users.models import User


class Command(BaseCommand):
    help = 'Initialize reports module with sample data'

    def handle(self, *args, **options):
        self.stdout.write('正在初始化报表模块数据...')
        
        # 创建报表分类
        categories_data = [
            {'name': '人事报表', 'code': 'employee', 'description': '员工相关统计报表'},
            {'name': '考勤报表', 'code': 'attendance', 'description': '考勤数据统计报表'},
            {'name': '薪资报表', 'code': 'salary', 'description': '薪资发放统计报表'},
            {'name': '绩效报表', 'code': 'performance', 'description': '绩效评估统计报表'},
        ]
        
        for category_data in categories_data:
            category, created = ReportCategory.objects.get_or_create(
                code=category_data['code'],
                defaults=category_data
            )
            if created:
                self.stdout.write(f'创建报表分类: {category.name}')
          # 获取管理员用户
        try:
            admin_user = User.objects.filter(user_type='admin').first()
            if not admin_user:
                admin_user = User.objects.filter(is_superuser=True).first()
            
            if admin_user:
                # 创建报表模板
                templates_data = [
                    {
                        'name': '员工基本信息统计表',
                        'code': 'employee_basic_stats',
                        'category': ReportCategory.objects.get(code='employee'),
                        'description': '统计员工基本信息、部门分布等',
                        'default_format': 'xlsx',
                        'created_by': admin_user,
                    },
                    {
                        'name': '月度考勤统计表',
                        'code': 'monthly_attendance_stats',
                        'category': ReportCategory.objects.get(code='attendance'),
                        'description': '统计员工月度考勤情况、迟到早退等',
                        'default_format': 'xlsx',
                        'created_by': admin_user,
                    },
                    {
                        'name': '月度薪资统计表',
                        'code': 'monthly_salary_stats',
                        'category': ReportCategory.objects.get(code='salary'),
                        'description': '统计员工月度薪资发放情况',
                        'default_format': 'xlsx',
                        'created_by': admin_user,
                    },
                    {
                        'name': '绩效评估统计表',
                        'code': 'performance_evaluation_stats',
                        'category': ReportCategory.objects.get(code='performance'),
                        'description': '统计员工绩效评估结果',
                        'default_format': 'xlsx',
                        'created_by': admin_user,
                    },
                ]
                
                for template_data in templates_data:
                    template, created = ReportTemplate.objects.get_or_create(
                        code=template_data['code'],
                        defaults=template_data
                    )
                    if created:
                        self.stdout.write(f'创建报表模板: {template.name}')
                
                # 创建一些示例系统日志
                log_data = [
                    {
                        'level': 'info',
                        'module': 'users',
                        'user': admin_user,
                        'message': '管理员登录系统',
                        'full_message': f'用户 {admin_user.username} 于 {timezone.now()} 登录系统',
                        'ip_address': '127.0.0.1',
                    },
                    {
                        'level': 'info',
                        'module': 'reports',
                        'user': admin_user,
                        'message': '初始化报表模块数据',
                        'full_message': '系统管理员初始化报表模块基础数据，包括分类和模板',
                        'ip_address': '127.0.0.1',
                    },
                    {
                        'level': 'info',
                        'module': 'system',
                        'user': None,
                        'message': '系统启动完成',
                        'full_message': 'HR管理系统启动完成，所有模块加载正常',
                        'ip_address': '127.0.0.1',
                    },
                ]
                
                for log_item in log_data:
                    SystemLog.objects.create(**log_item)
                
                self.stdout.write(self.style.SUCCESS('报表模块数据初始化完成！'))
            else:
                self.stdout.write(self.style.WARNING('未找到管理员用户，请先创建管理员用户'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'初始化失败: {str(e)}'))
