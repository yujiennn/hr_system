"""
初始化薪资计算配置的管理命令
"""
from django.core.management.base import BaseCommand
from salary.models import SalaryConfig


class Command(BaseCommand):
    help = '初始化默认薪资计算配置'

    def handle(self, *args, **options):
        # 检查是否已存在配置
        if SalaryConfig.objects.exists():
            self.stdout.write(
                self.style.WARNING('薪资配置已存在，跳过初始化。')
            )
            # 列出现有配置
            for config in SalaryConfig.objects.all():
                status = '(启用)' if config.is_active else '(禁用)'
                self.stdout.write(f'  - {config.name} {status}')
            return

        # 创建默认配置
        config = SalaryConfig.objects.create(
            name='默认配置',
            is_active=True,
            
            # 全勤奖
            full_attendance_bonus=500.00,
            
            # 绩效等级分数线
            performance_level_a_min=90,
            performance_level_b_min=80,
            performance_level_c_min=60,
            
            # 绩效系数
            performance_level_a_coefficient=1.5,
            performance_level_b_coefficient=1.2,
            performance_level_c_coefficient=1.0,
            performance_level_d_coefficient=0.5,
            
            # 绩效奖金基数比例（基本工资的20%作为绩效奖金基数）
            performance_bonus_base_rate=0.2,
            
            # 请假扣款配置
            sick_leave_free_days=2,      # 病假免扣天数
            sick_leave_deduction_rate=0.5,  # 病假扣款比例（超过免扣天数后）
            personal_leave_deduction_rate=1.0,  # 事假全额扣款
            
            # 迟到扣款配置
            late_deduction_minor=20.00,   # 轻微迟到（≤30分钟）
            late_deduction_major=50.00,   # 严重迟到（>30分钟）
            late_threshold_minutes=30,     # 迟到严重阈值
            
            # 缺勤扣款比例
            absence_deduction_rate=1.0,   # 缺勤按日薪100%扣款
            
            # 每月工作日（用于计算日薪）
            work_days_per_month=22,
        )

        self.stdout.write(
            self.style.SUCCESS(f'成功创建默认薪资配置: {config.name}')
        )
        
        # 输出配置详情
        self.stdout.write('\n配置详情:')
        self.stdout.write(f'  全勤奖: ¥{config.full_attendance_bonus}')
        self.stdout.write(f'  绩效奖金基数: 基本工资 × {config.performance_bonus_base_rate * 100}%')
        self.stdout.write(f'  A级(≥{config.performance_level_a_min}分): 系数 {config.performance_level_a_coefficient}')
        self.stdout.write(f'  B级(≥{config.performance_level_b_min}分): 系数 {config.performance_level_b_coefficient}')
        self.stdout.write(f'  C级(≥{config.performance_level_c_min}分): 系数 {config.performance_level_c_coefficient}')
        self.stdout.write(f'  D级(<{config.performance_level_c_min}分): 系数 {config.performance_level_d_coefficient}')
        self.stdout.write(f'  病假免扣: {config.sick_leave_free_days}天')
        self.stdout.write(f'  每月工作日: {config.work_days_per_month}天')
