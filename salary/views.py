from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from django.db import models
from django.http import HttpResponse
from .models import SalaryRecord, SalaryStructure, SalaryItem, SalaryConfig
from .serializers import (SalaryRecordSerializer, SalaryStructureSerializer, 
                         SalaryItemSerializer, SalaryConfigSerializer, SalaryRecordCreateSerializer)
from users.models import User
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from io import BytesIO


class SalaryConfigViewSet(viewsets.ModelViewSet):
    """薪资配置视图集"""
    queryset = SalaryConfig.objects.all()
    serializer_class = SalaryConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """只有管理员和财务部门可以管理薪资配置"""
        user = self.request.user
        if user.is_admin or user.is_finance_department:
            return SalaryConfig.objects.all()
        return SalaryConfig.objects.none()
    
    @action(detail=False, methods=['get'], url_path='active')
    def get_active_config(self, request):
        """获取当前启用的配置"""
        config = SalaryConfig.get_active_config()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """激活指定配置"""
        user = request.user
        if not (user.is_admin or user.is_finance_department):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        config = self.get_object()
        # 先将所有配置设为非活动
        SalaryConfig.objects.update(is_active=False)
        # 激活当前配置
        config.is_active = True
        config.save()
        
        return Response({'message': f'配置 "{config.name}" 已激活'})


class SalaryRecordViewSet(viewsets.ModelViewSet):
    queryset = SalaryRecord.objects.all()  # 基础queryset，实际查询由get_queryset方法控制
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return SalaryRecordCreateSerializer
        return SalaryRecordSerializer
    
    def get_queryset(self):
        """根据用户角色返回相应的薪资数据"""
        user = self.request.user
        
        if user.is_admin:
            # 管理员可以查看所有薪资
            return SalaryRecord.objects.all().select_related('user', 'manager', 'finance_approver', 'rejected_by')
        elif user.is_manager:
            # 经理可以查看本部门员工薪资
            return SalaryRecord.objects.filter(user__department=user.department).select_related('user', 'manager', 'finance_approver', 'rejected_by')
        else:
            # 普通员工：
            # - 财务部员工可以看全部（用于管理薪资）
            # - 非财务部员工只能看自己的
            if user.is_finance_department:
                return SalaryRecord.objects.all().select_related('user', 'manager', 'finance_approver', 'rejected_by')
            else:
                return SalaryRecord.objects.filter(user=user).select_related('user', 'manager', 'finance_approver', 'rejected_by')
    
    def get_permissions(self):
        """根据操作类型设置不同的权限"""
        if self.action in ['create', 'update', 'partial_update']:
            # 只有财务部员工和管理员可以创建/更新薪资记录
            if self.request.user.is_finance_department or self.request.user.is_admin:
                return [permissions.IsAuthenticated()]
            else:
                return [permissions.IsAdminUser()]  # 拒绝其他角色
        elif self.action == 'destroy':
            # 只有管理员可以删除薪资记录
            return [permissions.IsAdminUser()]
        elif self.action in ['manager_review', 'finance_approve', 'pay']:
            # 这些操作有各自的权限检查
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """创建薪资记录时添加权限检查"""
        user = self.request.user
        
        # 只有财务部员工和管理员可以创建
        if not (user.is_finance_department or user.is_admin):
            raise serializers.ValidationError('只有财务部员工可以创建薪资记录')
        
        serializer.save()
    
    def perform_update(self, serializer):
        """更新薪资记录时添加权限检查"""
        user = self.request.user
        salary_record = self.get_object()
        
        # 只有财务部员工和管理员可以编辑草稿状态的薪资
        if not (user.is_finance_department or user.is_admin):
            raise serializers.ValidationError('只有财务部员工可以编辑薪资记录')
        
        if salary_record.status != 'draft':
            raise serializers.ValidationError('只能编辑草稿状态的薪资记录')
        
        serializer.save()
    
    @action(detail=False, methods=['get'], url_path='my-records')
    def my_records(self, request):
        """获取当前用户的薪资记录"""
        user = request.user
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        
        queryset = SalaryRecord.objects.filter(user=user)
        
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
            
        queryset = queryset.order_by('-year', '-month')
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })
    
    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate_salary(self, request):
        """
        自动计算员工工资（根据绩效和考勤）
        请求参数:
        - user_id: 员工ID
        - year: 年份
        - month: 月份
        - basic_salary: 基本工资（可选，默认从员工信息获取）
        - allowances: 津贴（可选）
        - overtime_pay: 加班费（可选）
        - social_security: 社保（可选）
        - housing_fund: 公积金（可选）
        """
        user = request.user
        
        # 权限检查：只有财务部员工和管理员可以计算工资
        if not (user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足，只有财务部门可以计算工资'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not all([user_id, year, month]):
            return Response({'error': '缺少必要参数：user_id, year, month'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': '员工不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否已存在该月的工资记录
        salary_record, created = SalaryRecord.objects.get_or_create(
            user=employee,
            year=int(year),
            month=int(month),
            defaults={
                'basic_salary': request.data.get('basic_salary', employee.base_salary or 0),
                'allowances': request.data.get('allowances', 0),
                'overtime_pay': request.data.get('overtime_pay', 0),
                'social_security': request.data.get('social_security', 0),
                'housing_fund': request.data.get('housing_fund', 0),
                'income_tax': request.data.get('income_tax', 0),
                'other_deductions': request.data.get('other_deductions', 0),
            }
        )
        
        if not created:
            # 如果记录已存在，检查状态
            if salary_record.status not in ['draft', 'rejected']:
                return Response({
                    'error': '该工资记录已在审批流程中，无法重新计算',
                    'current_status': salary_record.get_status_display()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新基本信息
            salary_record.basic_salary = request.data.get('basic_salary', salary_record.basic_salary)
            salary_record.allowances = request.data.get('allowances', salary_record.allowances)
            salary_record.overtime_pay = request.data.get('overtime_pay', salary_record.overtime_pay)
            salary_record.social_security = request.data.get('social_security', salary_record.social_security)
            salary_record.housing_fund = request.data.get('housing_fund', salary_record.housing_fund)
            salary_record.income_tax = request.data.get('income_tax', salary_record.income_tax)
            salary_record.other_deductions = request.data.get('other_deductions', salary_record.other_deductions)
            salary_record.save()
        
        # 自动计算绩效和考勤相关项
        try:
            salary_record.calculate_from_performance_and_attendance()
        except Exception as e:
            return Response({
                'error': f'计算过程出错: {str(e)}',
                'salary_record': SalaryRecordSerializer(salary_record).data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': '工资计算完成',
            'created': created,
            'salary_record': SalaryRecordSerializer(salary_record).data,
            'calculation_details': {
                'performance_score': salary_record.performance_score,
                'performance_level': salary_record.performance_level,
                'performance_coefficient': salary_record.performance_coefficient,
                'performance_bonus': float(salary_record.performance_bonus),
                'is_full_attendance': salary_record.is_full_attendance,
                'full_attendance_bonus': float(salary_record.full_attendance_bonus),
                'leave_days': salary_record.leave_days,
                'leave_deduction': float(salary_record.leave_deduction),
                'late_count': salary_record.late_count,
                'late_deduction': float(salary_record.late_deduction),
                'absence_count': salary_record.absence_count,
                'absence_deduction': float(salary_record.absence_deduction),
            }
        })
    
    @action(detail=False, methods=['post'], url_path='batch-calculate')
    def batch_calculate(self, request):
        """
        批量计算员工工资
        请求参数:
        - year: 年份
        - month: 月份
        - department_id: 部门ID（可选，不指定则计算所有员工）
        """
        user = request.user
        
        if not (user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        year = request.data.get('year')
        month = request.data.get('month')
        department_id = request.data.get('department_id')
        
        if not all([year, month]):
            return Response({'error': '缺少必要参数：year, month'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 获取要计算的员工列表
        employees = User.objects.filter(is_active=True, user_type='employee')
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        for employee in employees:
            try:
                # 检查是否已存在该月的工资记录且不在可编辑状态
                existing = SalaryRecord.objects.filter(
                    user=employee, year=year, month=month
                ).first()
                
                if existing and existing.status not in ['draft', 'rejected']:
                    results['skipped'].append({
                        'employee_id': employee.employee_id,
                        'name': employee.get_full_name(),
                        'reason': f'已在审批流程中 ({existing.get_status_display()})'
                    })
                    continue
                
                # 创建或获取工资记录
                salary_record, created = SalaryRecord.objects.get_or_create(
                    user=employee,
                    year=int(year),
                    month=int(month),
                    defaults={
                        'basic_salary': employee.base_salary or 0,
                    }
                )
                
                if not created:
                    salary_record.basic_salary = employee.base_salary or salary_record.basic_salary
                    salary_record.save()
                
                # 计算
                salary_record.calculate_from_performance_and_attendance()
                
                results['success'].append({
                    'employee_id': employee.employee_id,
                    'name': employee.get_full_name(),
                    'net_salary': float(salary_record.net_salary)
                })
                
            except Exception as e:
                results['failed'].append({
                    'employee_id': employee.employee_id,
                    'name': employee.get_full_name(),
                    'error': str(e)
                })
        
        return Response({
            'message': f'批量计算完成',
            'summary': {
                'total': len(employees),
                'success': len(results['success']),
                'failed': len(results['failed']),
                'skipped': len(results['skipped'])
            },
            'results': results
        })
    
    @action(detail=True, methods=['get'], url_path='attendance-summary')
    def attendance_summary(self, request, pk=None):
        """获取工资记录相关的考勤统计"""
        salary_record = self.get_object()
        
        return Response({
            'year': salary_record.year,
            'month': salary_record.month,
            'attendance': {
                'late_count': salary_record.late_count,
                'early_leave_count': salary_record.early_leave_count,
                'absence_count': salary_record.absence_count,
                'actual_work_days': salary_record.actual_work_days,
            },
            'leave': {
                'total_days': salary_record.leave_days,
                'sick_leave_days': salary_record.sick_leave_days,
                'personal_leave_days': salary_record.personal_leave_days,
                'other_leave_days': salary_record.other_leave_days,
            },
            'deductions': {
                'late_deduction': float(salary_record.late_deduction),
                'absence_deduction': float(salary_record.absence_deduction),
                'leave_deduction': float(salary_record.leave_deduction),
            },
            'full_attendance': {
                'is_full_attendance': salary_record.is_full_attendance,
                'bonus': float(salary_record.full_attendance_bonus),
            }
        })
    
    @action(detail=True, methods=['get'], url_path='performance-summary')
    def performance_summary(self, request, pk=None):
        """获取工资记录相关的绩效信息"""
        salary_record = self.get_object()
        
        performance_data = {
            'score': salary_record.performance_score,
            'level': salary_record.performance_level,
            'level_display': salary_record.get_performance_level_display() if salary_record.performance_level else None,
            'coefficient': salary_record.performance_coefficient,
            'bonus': float(salary_record.performance_bonus),
            'evaluation_id': salary_record.performance_evaluation_id,
        }
        
        # 如果有关联的绩效评估，获取更多详情
        if salary_record.performance_evaluation:
            evaluation = salary_record.performance_evaluation
            performance_data['evaluation_details'] = {
                'self_score': evaluation.self_evaluation_score,
                'manager_score': evaluation.manager_evaluation_score,
                'final_score': evaluation.final_score,
                'final_rating': evaluation.final_rating,
                'status': evaluation.status,
                'evaluator': evaluation.evaluator.get_full_name() if evaluation.evaluator else None,
            }
        
        return Response(performance_data)
    
    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        """重新计算指定的工资记录"""
        user = request.user
        
        if not (user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        salary_record = self.get_object()
        
        if salary_record.status not in ['draft', 'rejected']:
            return Response({
                'error': '只能重新计算草稿或已拒绝状态的工资记录'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            salary_record.calculate_from_performance_and_attendance()
            return Response({
                'message': '重新计算完成',
                'salary_record': SalaryRecordSerializer(salary_record).data
            })
        except Exception as e:
            return Response({
                'error': f'计算出错: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='pending-review')
    def pending_review(self, request):
        """获取待经理审核的薪资（经理专用）"""
        user = request.user
        
        if not user.is_manager and not user.is_admin:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        # 经理查看本部门draft的薪资
        if user.is_admin:
            queryset = SalaryRecord.objects.filter(status='draft')
        else:
            queryset = SalaryRecord.objects.filter(
                status='draft',
                user__department=user.department
            )
        
        queryset = queryset.select_related('user', 'user__department').order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })
    
    @action(detail=False, methods=['get'], url_path='pending-approval')
    def pending_approval(self, request):
        """获取待财务批准的薪资（财务专用）"""
        user = request.user
        
        if not user.is_finance_department and not user.is_admin:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        # 查看manager_reviewed的薪资
        queryset = SalaryRecord.objects.filter(status='manager_reviewed').select_related('user', 'manager').order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })
    
    @action(detail=True, methods=['post'], url_path='manager-review')
    def manager_review(self, request, pk=None):
        """经理审核薪资"""
        salary_record = self.get_object()
        user = request.user
        
        # 权限检查
        if not user.is_manager and not user.is_admin:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        if not user.is_admin and salary_record.user.department != user.department:
            return Response({'error': '只能审核本部门薪资'}, status=status.HTTP_403_FORBIDDEN)
        
        if salary_record.status != 'draft':
            return Response({'error': '只能审核草稿状态的薪资'}, status=status.HTTP_400_BAD_REQUEST)
        
        action = request.data.get('action')
        note = request.data.get('manager_note', '')
        
        if action == 'approve':
            salary_record.status = 'manager_reviewed'
            salary_record.manager = user
            salary_record.manager_note = note
            salary_record.manager_reviewed_at = timezone.now()
            salary_record.save()
            return Response({
                'status': '审核通过',
                'message': '薪资已提交财务批准'
            })
        elif action == 'reject':
            salary_record.status = 'rejected'
            salary_record.rejected_by = user
            salary_record.rejection_reason = note
            salary_record.rejected_at = timezone.now()
            salary_record.save()
            return Response({
                'status': '审核拒绝',
                'message': '薪资已拒绝，财务需重新编辑'
            })
        else:
            return Response({'error': 'action必须为approve或reject'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='finance-approve')
    def finance_approve(self, request, pk=None):
        """财务部门批准薪资（由财务部长或财务经理执行）"""
        salary_record = self.get_object()
        user = request.user
        
        # 权限检查：财务部员工或管理员可以批准
        if not (user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        if salary_record.status != 'manager_reviewed':
            return Response({'error': '只能批准经理已审核的薪资'}, status=status.HTTP_400_BAD_REQUEST)
        
        action = request.data.get('action')
        note = request.data.get('finance_note', '')
        
        if action == 'approve':
            salary_record.status = 'finance_approved'
            salary_record.finance_approver = user
            salary_record.finance_note = note
            salary_record.finance_approved_at = timezone.now()
            salary_record.save()
            return Response({
                'status': '批准成功',
                'message': '薪资已批准，可以发放'
            })
        elif action == 'reject':
            salary_record.status = 'rejected'
            salary_record.rejected_by = user
            salary_record.rejection_reason = note
            salary_record.rejected_at = timezone.now()
            salary_record.save()
            return Response({
                'status': '批准拒绝',
                'message': '薪资已拒绝，财务需重新编辑'
            })
        else:
            return Response({'error': 'action必须为approve或reject'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        """发放薪资（由财务部门执行）"""
        salary_record = self.get_object()
        user = request.user
        
        # 权限检查：财务部员工或管理员可以发放
        if not (user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        if salary_record.status != 'finance_approved':
            return Response({'error': '只能发放已批准的薪资'}, status=status.HTTP_400_BAD_REQUEST)
        
        pay_date = request.data.get('pay_date')
        if not pay_date:
            return Response({'error': '需要提供发放日期'}, status=status.HTTP_400_BAD_REQUEST)
        
        salary_record.status = 'paid'
        salary_record.pay_date = pay_date
        salary_record.paid_by = user
        salary_record.save()
        
        return Response({
            'status': '发放成功',
            'message': f'薪资已于{pay_date}发放'
        })
    
    @action(detail=False, methods=['get'], url_path='department-records')
    def department_records(self, request):
        """获取部门薪资记录（经理、财务部员工、管理员专用）"""
        user = request.user
        
        if not (user.is_manager or user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', None)
        employee_id = request.query_params.get('employee_id', None)
        
        # 基础查询
        if user.is_admin:
            queryset = SalaryRecord.objects.filter(year=year)
        elif user.is_finance_department:
            # 财务部员工可以看所有部门的薪资
            queryset = SalaryRecord.objects.filter(year=year)
        else:
            # 经理只能看本部门
            queryset = SalaryRecord.objects.filter(
                year=year, 
                user__department=user.department
            )
        
        # 进一步筛选
        if month:
            queryset = queryset.filter(month=month)
        if employee_id:
            queryset = queryset.filter(user__employee_id=employee_id)
            
        queryset = queryset.select_related('user', 'user__department').order_by('-year', '-month', 'user__employee_id')
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })

    @action(detail=False, methods=['get'], url_path='department-employees')
    def department_employees(self, request):
        """获取部门员工列表（经理、财务部员工、管理员专用）"""
        user = request.user
        
        if not (user.is_manager or user.is_finance_department or user.is_admin):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        if user.is_admin:
            # 管理员可以获取所有员工
            employees = User.objects.filter(is_active=True, user_type='employee')
        elif user.is_finance_department:
            # 财务部员工可以获取所有员工
            employees = User.objects.filter(is_active=True, user_type='employee')
        else:
            # 经理只能获取本部门员工
            employees = User.objects.filter(
                department=user.department, 
                is_active=True, 
                user_type='employee'
            )
        
        employee_data = []
        for emp in employees:
            employee_data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': emp.get_full_name() or emp.username,
                'department': emp.department.name if emp.department else '',
                'position': emp.position or '',
                'base_salary': emp.base_salary or 0
            })
        
        return Response({'employees': employee_data})

    @action(detail=True, methods=['get'], url_path='export')
    def export_record(self, request, pk=None):
        """导出单个薪资记录"""
        record = self.get_object()
        
        # 权限检查：财务部员工 + 管理员 + 经理 + 员工本人
        user = request.user
        if not (user.is_admin or user.is_manager or user.is_finance_department or record.user == user):
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        # 创建Excel工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "工资单"
          # 获取员工信息
        user = record.user
        department = user.department
        
        # 设置标题
        ws['A1'] = f"{record.year}年{record.month}月工资单"
        ws.merge_cells('A1:B1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        
        # 员工基本信息
        info_data = [
            ('员工工号', user.employee_id or user.username),
            ('员工姓名', user.get_full_name() or user.username),
            ('所属部门', department.name if department else '未分配'),
            ('发放年月', f"{record.year}年{record.month}月"),
            ('', ''),  # 空行
            ('基本工资', float(record.basic_salary) if record.basic_salary else 0),
            ('绩效奖金', float(record.performance_bonus) if record.performance_bonus else 0),
            ('加班费', float(record.overtime_pay) if record.overtime_pay else 0),
            ('津贴', float(record.allowances) if record.allowances else 0),
            ('应发工资', float(record.gross_salary) if record.gross_salary else 0),
            ('', ''),  # 空行
            ('社保', float(record.social_security) if record.social_security else 0),
            ('公积金', float(record.housing_fund) if record.housing_fund else 0),
            ('个人所得税', float(record.income_tax) if record.income_tax else 0),
            ('其他扣除', float(record.other_deductions) if record.other_deductions else 0),
            ('', ''),  # 空行
            ('实发工资', float(record.net_salary) if record.net_salary else 0),
        ]
        
        # 填充数据
        for row, (label, value) in enumerate(info_data, start=3):
            if label:  # 跳过空行
                ws.cell(row=row, column=1, value=label)
                ws.cell(row=row, column=2, value=value)
                
                # 设置样式
                if label in ['应发工资', '实发工资']:
                    ws.cell(row=row, column=1).font = Font(bold=True)
                    ws.cell(row=row, column=2).font = Font(bold=True)
                
                if isinstance(value, (int, float)) and value != 0:
                    ws.cell(row=row, column=2).number_format = '#,##0.00'
        
        # 设置列宽
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 15
        
        # 保存到内存
        output = BytesIO()
        wb.save(output)
        output.seek(0)
          # 生成文件名
        employee_id = user.employee_id or user.username
        filename = f"工资单_{employee_id}_{record.year}年{record.month}月.xlsx"
        
        # 返回Excel文件
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [permissions.IsAuthenticated]


class SalaryItemViewSet(viewsets.ModelViewSet):
    queryset = SalaryItem.objects.all()
    serializer_class = SalaryItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class MySalaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', None)
        
        queryset = SalaryRecord.objects.filter(user=user, year=year)
        
        if month:
            queryset = queryset.filter(month=month)
            
        salary_records = queryset.order_by('-year', '-month')
        serializer = SalaryRecordSerializer(salary_records, many=True)
        
        # 如果指定了月份，返回当月详情
        if month and salary_records.exists():
            current_salary = salary_records.first()
            return Response({
                'current_salary': SalaryRecordSerializer(current_salary).data,
                'salary_records': serializer.data
            })
        
        return Response({'salary_records': serializer.data})


class PayslipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            user = request.user
            salary_record = SalaryRecord.objects.get(pk=pk)
            
            # 检查权限：员工只能查看自己的工资单
            if not user.is_admin and not user.is_manager and salary_record.user != user:
                return Response({'error': '无权查看此工资单'}, status=status.HTTP_403_FORBIDDEN)
            
            # 经理只能查看本部门员工的工资单
            if user.is_manager and not user.is_admin and salary_record.user.department != user.department:
                return Response({'error': '无权查看此工资单'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = SalaryRecordSerializer(salary_record)
            return Response({'payslip': serializer.data})
            
        except SalaryRecord.DoesNotExist:
            return Response({'error': '工资单不存在'}, status=status.HTTP_404_NOT_FOUND)


class SalaryStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        department_id = request.query_params.get('department')
        employee_id = request.query_params.get('employee')
        
        # 根据用户权限确定查询范围
        if user.is_admin:
            queryset = SalaryRecord.objects.filter(year=year)
        elif user.is_manager:
            queryset = SalaryRecord.objects.filter(year=year, user__department=user.department)
        else:
            # 普通员工只能查看自己的统计
            queryset = SalaryRecord.objects.filter(year=year, user=user)
        
        # 进一步筛选
        if department_id and (user.is_admin):
            queryset = queryset.filter(user__department_id=department_id)
        
        if employee_id and (user.is_admin or user.is_manager):
            queryset = queryset.filter(user__employee_id=employee_id)
        
        # 计算统计数据
        statistics = queryset.aggregate(
            total_gross_salary=Sum('gross_salary'),
            total_net_salary=Sum('net_salary'),
            avg_gross_salary=Avg('gross_salary'),
            avg_net_salary=Avg('net_salary'),
            count=Count('id')
        )
        
        # 按月份统计
        monthly_stats = queryset.values('month').annotate(
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'statistics': {
                'year': year,
                'total_gross_salary': statistics['total_gross_salary'] or 0,
                'total_net_salary': statistics['total_net_salary'] or 0,
                'avg_gross_salary': statistics['avg_gross_salary'] or 0,
                'avg_net_salary': statistics['avg_net_salary'] or 0,
                'total_records': statistics['count'] or 0,
                'monthly_stats': list(monthly_stats)
            }
        })


class PayslipsView(APIView):
    """工资单列表视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        
        queryset = SalaryRecord.objects.filter(user=user, year=year).order_by('-year', '-month')
        serializer = SalaryRecordSerializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })


class SalaryExportView(APIView):
    """薪资导出视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month')
        employee_id = request.query_params.get('employee_id')
        
        # 根据用户权限确定查询范围
        if user.is_admin:
            queryset = SalaryRecord.objects.filter(year=year)
        elif user.is_manager:
            queryset = SalaryRecord.objects.filter(year=year, user__department=user.department)
        else:
            queryset = SalaryRecord.objects.filter(year=year, user=user)
        
        # 添加月份过滤
        if month:
            queryset = queryset.filter(month=month)
              # 添加员工过滤
        if employee_id:
            queryset = queryset.filter(user__employee_id=employee_id)
          # 预加载相关数据
        queryset = queryset.select_related('user', 'user__department').order_by('user__employee_id', 'year', 'month')
        
        # 创建Excel工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "薪资报表"
        
        # 设置标题
        title = f"{year}年"
        if month:
            title += f"{month}月"
        title += "薪资报表"
        
        ws['A1'] = title
        ws.merge_cells('A1:N1')
        
        # 设置标题样式
        title_font = Font(size=16, bold=True)
        title_alignment = Alignment(horizontal='center', vertical='center')
        title_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        ws['A1'].font = Font(size=16, bold=True, color='FFFFFF')
        ws['A1'].alignment = title_alignment
        ws['A1'].fill = title_fill
        
        # 设置表头
        headers = [
            '员工工号', '员工姓名', '部门', '年份', '月份',
            '基本工资', '绩效奖金', '加班费', '津贴',
            '应发工资', '社保', '公积金', '个税',
            '其他扣除', '实发工资'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
          # 填充数据
        row_num = 3
        for record in queryset:
            data = [
                record.user.employee_id or record.user.username,
                record.user.get_full_name() or record.user.username,
                record.user.department.name if record.user.department else '未分配',
                record.year,
                record.month,
                float(record.basic_salary) if record.basic_salary else 0,
                float(record.performance_bonus) if record.performance_bonus else 0,
                float(record.overtime_pay) if record.overtime_pay else 0,
                float(record.allowances) if record.allowances else 0,
                float(record.gross_salary) if record.gross_salary else 0,
                float(record.social_security) if record.social_security else 0,
                float(record.housing_fund) if record.housing_fund else 0,
                float(record.income_tax) if record.income_tax else 0,
                float(record.other_deductions) if record.other_deductions else 0,
                float(record.net_salary) if record.net_salary else 0,
            ]
            
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col, value=value)
                if col >= 6:  # 金额列
                    cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            row_num += 1
          # 设置列宽
        column_widths = [12, 15, 15, 8, 8, 12, 12, 10, 10, 12, 10, 10, 10, 10, 12]
        for col, width in enumerate(column_widths, 1):
            column_letter = chr(64 + col)  # A=65, B=66, etc.
            ws.column_dimensions[column_letter].width = width
        
        # 设置边框
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for row in ws.iter_rows(min_row=1, max_row=row_num-1, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border
        
        # 保存到内存
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # 生成文件名
        filename = f"薪资报表_{year}年"
        if month:
            filename += f"{month}月"
        if employee_id:
            filename += f"_{employee_id}"
        filename += ".xlsx"
        
        # 返回Excel文件
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
