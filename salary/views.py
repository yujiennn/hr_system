from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from django.db import models
from django.http import HttpResponse
from .models import SalaryRecord, SalaryStructure, SalaryItem
from .serializers import SalaryRecordSerializer, SalaryStructureSerializer, SalaryItemSerializer
from users.models import User
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from io import BytesIO


class SalaryRecordViewSet(viewsets.ModelViewSet):
    queryset = SalaryRecord.objects.all()  # 基础queryset，实际查询由get_queryset方法控制
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return SalaryRecord.objects.all()
        elif user.is_manager:
            # 经理可以查看本部门员工薪资
            return SalaryRecord.objects.filter(user__department=user.department)
        else:
            # 普通员工只能查看自己的薪资
            return SalaryRecord.objects.filter(user=user)
    
    def get_permissions(self):
        """根据操作类型设置不同的权限"""
        if self.action in ['create', 'update', 'partial_update']:
            # 只有管理员和经理可以创建/更新薪资记录
            if self.request.user.is_admin or self.request.user.is_manager:
                return [permissions.IsAuthenticated()]
            else:
                return [permissions.IsAdminUser()]  # 拒绝普通员工
        elif self.action == 'destroy':
            # 只有管理员可以删除薪资记录
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """创建薪资记录时添加权限检查"""
        user = self.request.user
        target_user_id = self.request.data.get('user')
        
        if user.is_manager and not user.is_admin:
            # 经理只能为本部门员工创建薪资记录
            try:
                target_user = User.objects.get(id=target_user_id)
                if target_user.department != user.department:
                    raise serializers.ValidationError('无权为其他部门员工创建薪资记录')
            except User.DoesNotExist:
                raise serializers.ValidationError('目标用户不存在')
        
        serializer.save()
    
    def perform_update(self, serializer):
        """更新薪资记录时添加权限检查"""
        user = self.request.user
        salary_record = self.get_object()
        
        if user.is_manager and not user.is_admin:
            # 经理只能更新本部门员工的薪资记录
            if salary_record.user.department != user.department:
                raise serializers.ValidationError('无权修改其他部门员工的薪资记录')
        
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
    
    @action(detail=False, methods=['get'], url_path='department-records')
    def department_records(self, request):
        """获取部门薪资记录（经理专用）"""
        user = request.user
        
        if not user.is_manager and not user.is_admin:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', None)
        employee_id = request.query_params.get('employee_id', None)
        
        # 基础查询
        if user.is_admin:
            queryset = SalaryRecord.objects.filter(year=year)
        else:
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
        """获取部门员工列表（用于创建薪资记录）"""
        user = request.user
        
        if not user.is_manager and not user.is_admin:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        if user.is_admin:
            # 管理员可以获取所有员工
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
        
        # 权限检查
        user = request.user
        if not user.is_admin and not user.is_manager and record.user != user:
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
