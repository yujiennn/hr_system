from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
import os
import json
from datetime import datetime, timedelta
from .models import ReportCategory, ReportTemplate, Report, ReportSchedule, SystemLog
from .serializers import (
    ReportCategorySerializer, ReportTemplateSerializer, ReportSerializer,
    ReportScheduleSerializer, SystemLogSerializer, ReportGenerationSerializer,
    LogQuerySerializer
)
from users.models import User
from attendance.models import AttendanceRecord
from salary.models import SalaryRecord
from performance.models import PerformanceEvaluation


class ReportCategoryViewSet(viewsets.ModelViewSet):
    """报表分类视图集"""
    queryset = ReportCategory.objects.all()
    serializer_class = ReportCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """报表模板视图集"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportViewSet(viewsets.ModelViewSet):
    """报表记录视图集"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Report.objects.all()
        else:
            return Report.objects.filter(generated_by=user)
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载报表文件"""
        report = self.get_object()
        
        if not report.file_path or not os.path.exists(report.file_path):
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with open(report.file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{report.name}.{report.file_format}"'
                return response
        except Exception as e:
            return Response({'error': '文件读取失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """定时报表任务视图集"""
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ReportSchedule.objects.all()
        else:
            return ReportSchedule.objects.filter(created_by=user)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
            if not self.request.user.is_admin:
                self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """系统日志视图集"""
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not (user.is_admin or user.is_manager):
            # 普通员工只能看到自己相关的日志
            return SystemLog.objects.filter(user=user)
        return SystemLog.objects.all()
    
    def get_permissions(self):
        # 只有管理员和经理可以查看系统日志
        if not (self.request.user.is_admin or self.request.user.is_manager):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """搜索日志"""
        serializer = LogQuerySerializer(data=request.data)
        if serializer.is_valid():
            queryset = self.get_queryset()
            
            # 应用筛选条件
            if serializer.validated_data.get('level'):
                queryset = queryset.filter(level=serializer.validated_data['level'])
            
            if serializer.validated_data.get('module'):
                queryset = queryset.filter(module=serializer.validated_data['module'])
            
            if serializer.validated_data.get('user_id'):
                queryset = queryset.filter(user_id=serializer.validated_data['user_id'])
            
            if serializer.validated_data.get('start_date'):
                queryset = queryset.filter(timestamp__gte=serializer.validated_data['start_date'])
            
            if serializer.validated_data.get('end_date'):
                queryset = queryset.filter(timestamp__lte=serializer.validated_data['end_date'])
            
            if serializer.validated_data.get('keyword'):
                keyword = serializer.validated_data['keyword']
                queryset = queryset.filter(
                    Q(message__icontains=keyword) | Q(full_message__icontains=keyword)
                )
            
            if serializer.validated_data.get('ip_address'):
                queryset = queryset.filter(ip_address=serializer.validated_data['ip_address'])
            
            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                response_serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(response_serializer.data)
            
            response_serializer = self.get_serializer(queryset, many=True)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """日志统计"""
        queryset = self.get_queryset()
        
        # 按级别统计
        level_stats = queryset.values('level').annotate(count=Count('id'))
        
        # 按模块统计
        module_stats = queryset.values('module').annotate(count=Count('id'))
        
        # 按时间统计（最近7天）
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        daily_stats = []
        
        for i in range(7):
            date = start_date + timedelta(days=i)
            count = queryset.filter(
                timestamp__date=date.date()
            ).count()
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # 总数统计
        total_count = queryset.count()
        
        return Response({
            'total_count': total_count,
            'level_stats': list(level_stats),
            'module_stats': list(module_stats),
            'daily_stats': daily_stats
        })
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """清理日志"""
        if not request.user.is_admin:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        
        strategy = request.data.get('strategy', 'by_time')
        
        if strategy == 'by_time':
            retention_days = int(request.data.get('retention_days', 30))
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            deleted_count = SystemLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        elif strategy == 'by_count':
            retention_count = int(request.data.get('retention_count', 10000))
            # 保留最新的记录
            ids_to_keep = SystemLog.objects.order_by('-timestamp')[:retention_count].values_list('id', flat=True)
            deleted_count = SystemLog.objects.exclude(id__in=ids_to_keep).delete()[0]
        elif strategy == 'by_level':
            levels = request.data.get('levels', ['debug'])
            deleted_count = SystemLog.objects.filter(level__in=levels).delete()[0]
        else:
            return Response({'error': '无效的清理策略'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': f'已清理 {deleted_count} 条日志'})


class ReportGenerationView(APIView):
    """报表生成视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ReportGenerationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                template = ReportTemplate.objects.get(id=serializer.validated_data['template_id'])
                
                # 创建报表记录
                report = Report.objects.create(
                    name=serializer.validated_data['name'],
                    template=template,
                    parameters=serializer.validated_data['parameters'],
                    file_format=serializer.validated_data['format'],
                    generated_by=request.user,
                    status='processing'
                )
                
                # 这里应该调用异步任务来生成报表
                # 暂时模拟生成成功
                report.status = 'completed'
                report.completed_at = timezone.now()
                report.file_size = 1024 * 1024  # 模拟1MB
                report.save()
                
                return Response({
                    'message': '报表生成任务已启动',
                    'report_id': report.id
                }, status=status.HTTP_201_CREATED)
            
            except ReportTemplate.DoesNotExist:
                return Response({'error': '报表模板不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataStatisticsView(APIView):
    """数据统计视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 员工统计
        employee_stats = self._get_employee_statistics(user)
        
        # 考勤统计
        attendance_stats = self._get_attendance_statistics(user)
        
        # 薪资统计
        salary_stats = self._get_salary_statistics(user)
        
        # 绩效统计
        performance_stats = self._get_performance_statistics(user)
        
        return Response({
            'employee': employee_stats,
            'attendance': attendance_stats,
            'salary': salary_stats,
            'performance': performance_stats
        })
    
    def _get_employee_statistics(self, user):
        """获取员工统计数据"""
        if user.is_admin:
            queryset = User.objects.all()
        elif user.is_manager:
            queryset = User.objects.filter(department=user.department)
        else:
            return {'total': 1, 'active': 1, 'new_this_month': 0}
        
        total = queryset.count()
        active = queryset.filter(is_active_employee=True).count()
        
        # 本月新入职
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = queryset.filter(hire_date__gte=start_of_month).count()
        
        return {
            'total': total,
            'active': active,
            'new_this_month': new_this_month
        }
    
    def _get_attendance_statistics(self, user):
        """获取考勤统计数据"""
        if user.is_admin:
            queryset = AttendanceRecord.objects.all()
        elif user.is_manager:
            queryset = AttendanceRecord.objects.filter(user__department=user.department)
        else:
            queryset = AttendanceRecord.objects.filter(user=user)
        
        # 本月数据
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_queryset = queryset.filter(clock_time__gte=start_of_month)
        
        total_records = monthly_queryset.count()
        late_records = monthly_queryset.filter(status='late').count()
        early_records = monthly_queryset.filter(status='early').count()
        
        return {
            'total_records': total_records,
            'late_records': late_records,
            'early_records': early_records,
            'attendance_rate': round((total_records - late_records - early_records) / max(total_records, 1) * 100, 1)
        }
    
    def _get_salary_statistics(self, user):
        """获取薪资统计数据"""
        if user.is_admin:
            queryset = SalaryRecord.objects.all()
        elif user.is_manager:
            queryset = SalaryRecord.objects.filter(user__department=user.department)
        else:
            queryset = SalaryRecord.objects.filter(user=user)
        
        # 本年度数据
        current_year = timezone.now().year
        yearly_queryset = queryset.filter(year=current_year)
        
        stats = yearly_queryset.aggregate(
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            avg_gross=Avg('gross_salary'),
            avg_net=Avg('net_salary'),
            count=Count('id')
        )
        
        return {
            'total_gross_salary': stats['total_gross'] or 0,
            'total_net_salary': stats['total_net'] or 0,
            'average_gross_salary': stats['avg_gross'] or 0,
            'average_net_salary': stats['avg_net'] or 0,
            'total_records': stats['count'] or 0
        }
    
    def _get_performance_statistics(self, user):
        """获取绩效统计数据"""
        if user.is_admin:
            queryset = PerformanceEvaluation.objects.all()
        elif user.is_manager:
            queryset = PerformanceEvaluation.objects.filter(user__department=user.department)
        else:
            queryset = PerformanceEvaluation.objects.filter(user=user)
        
        # 本年度数据
        current_year = timezone.now().year
        yearly_queryset = queryset.filter(created_at__year=current_year)
        
        total_evaluations = yearly_queryset.count()
        completed_evaluations = yearly_queryset.filter(status='finalized').count()
        avg_score = yearly_queryset.filter(final_score__isnull=False).aggregate(
            avg=Avg('final_score')
        )['avg'] or 0
        
        return {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'completion_rate': round(completed_evaluations / max(total_evaluations, 1) * 100, 1),
            'average_score': round(avg_score, 1)
        }
