from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from .models import LeaveApplication, LeaveType, LeaveBalance
from .serializers import LeaveApplicationSerializer, LeaveTypeSerializer, LeaveBalanceSerializer, LeaveApprovalSerializer


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    queryset = LeaveApplication.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return LeaveApplication.objects.all()
        elif user.is_manager:
            # 部门经理可以看到本部门所有员工的请假申请
            return LeaveApplication.objects.filter(
                user__department=user.department
            )
        else:
            # 普通员工只能看到自己的请假申请
            return LeaveApplication.objects.filter(user=user)
    
    def perform_create(self, serializer):
        # 创建请假申请时，自动设置申请人为当前用户
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_application = self.get_object()
        serializer = LeaveApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            # 只有管理员和部门经理能审批
            user = request.user
            if not (user.is_admin or user.is_manager):
                return Response({'error': '你没有权限进行审批'}, status=status.HTTP_403_FORBIDDEN)
            
            # 检查申请状态
            if leave_application.status != 'pending':
                return Response({'error': '只能审批待审批的请假申请'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新审批状态
            with transaction.atomic():
                leave_application.status = serializer.validated_data['status']
                leave_application.approver = user
                leave_application.approval_note = serializer.validated_data.get('approval_note', '')
                leave_application.approved_at = timezone.now()
                leave_application.save()
                
                # 如果批准请假，更新请假余额
                if leave_application.status == 'approved':
                    current_year = timezone.now().year
                    leave_balance, created = LeaveBalance.objects.get_or_create(
                        user=leave_application.user,
                        leave_type=leave_application.leave_type,
                        year=current_year,
                        defaults={'total_days': leave_application.leave_type.max_days_per_year}
                    )
                    
                    leave_balance.used_days += leave_application.days
                    leave_balance.save()
            
            return Response({'message': '审批成功', 'status': leave_application.status})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        leave_application = self.get_object()
        
        # 只能取消自己的申请
        if leave_application.user != request.user and not request.user.is_admin:
            return Response({'error': '你没有权限取消此请假申请'}, status=status.HTTP_403_FORBIDDEN)
        
        # 只能取消待审批或已批准但未开始的请假
        if leave_application.status not in ['pending', 'approved']:
            return Response({'error': '只能取消待审批或已批准的请假申请'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果请假已经开始，不能取消
        if leave_application.status == 'approved' and leave_application.start_date <= timezone.now().date():
            return Response({'error': '请假已经开始，不能取消'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新为已取消状态
        with transaction.atomic():
            # 如果是已批准的请假被取消，需要恢复请假余额
            if leave_application.status == 'approved':
                current_year = timezone.now().year
                leave_balance = LeaveBalance.objects.get(
                    user=leave_application.user,
                    leave_type=leave_application.leave_type,
                    year=current_year
                )
                
                leave_balance.used_days -= leave_application.days
                leave_balance.save()
            
            leave_application.status = 'cancelled'
            leave_application.save()
        
        return Response({'message': '请假申请已取消'})


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveTypeSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以创建、修改和删除请假类型
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveBalanceSerializer
    
    def get_queryset(self):
        user = self.request.user
        year = self.request.query_params.get('year', timezone.now().year)
        
        if user.is_admin:
            queryset = LeaveBalance.objects.filter(year=year)
        elif user.is_manager:
            # 部门经理可以看到本部门所有员工的请假余额
            queryset = LeaveBalance.objects.filter(
                user__department=user.department,
                year=year
            )
        else:
            # 普通员工只能看到自己的请假余额
            queryset = LeaveBalance.objects.filter(user=user, year=year)
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以创建、修改和删除请假余额
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class MyLeaveApplicationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        
        # 获取指定年份的请假申请
        applications = LeaveApplication.objects.filter(
            user=user,
            start_date__year=year
        ).order_by('-created_at')
        
        serializer = LeaveApplicationSerializer(applications, many=True)
        
        return Response({
            'applications': serializer.data,
            'year': year
        })


class ApproveLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # 只有管理员和部门经理能审批
        user = request.user
        if not (user.is_admin or user.is_manager):
            return Response({'error': '你没有权限进行审批'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            leave_application = LeaveApplication.objects.get(pk=pk)
        except LeaveApplication.DoesNotExist:
            return Response({'error': '请假申请不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 部门经理只能审批本部门员工的请假
        if user.is_manager and leave_application.user.department != user.department:
            return Response({'error': '你没有权限审批其他部门员工的请假'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查申请状态
        if leave_application.status != 'pending':
            return Response({'error': '只能审批待审批的请假申请'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeaveApprovalSerializer(data=request.data)
        if serializer.is_valid():
            # 更新审批状态
            with transaction.atomic():
                leave_application.status = serializer.validated_data['status']
                leave_application.approver = user
                leave_application.approval_note = serializer.validated_data.get('approval_note', '')
                leave_application.approved_at = timezone.now()
                leave_application.save()
                
                # 如果批准请假，更新请假余额
                if leave_application.status == 'approved':
                    current_year = timezone.now().year
                    leave_balance, created = LeaveBalance.objects.get_or_create(
                        user=leave_application.user,
                        leave_type=leave_application.leave_type,
                        year=current_year,
                        defaults={'total_days': leave_application.leave_type.max_days_per_year}
                    )
                    
                    leave_balance.used_days += leave_application.days
                    leave_balance.save()
            
            return Response({'message': '审批成功', 'status': leave_application.status})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        
        # 管理员和经理可以查看部门或全公司统计
        if user.is_admin or user.is_manager:
            department_id = request.query_params.get('department')
            employee_id = request.query_params.get('employee')
            
            if employee_id:
                # 查看指定员工的统计
                try:
                    from users.models import User
                    target_user = User.objects.get(employee_id=employee_id)
                    users = [target_user]
                except User.DoesNotExist:
                    return Response({'error': '找不到该员工'}, status=status.HTTP_404_NOT_FOUND)
            elif department_id:
                # 查看指定部门的统计
                try:
                    from users.models import Department
                    department = Department.objects.get(id=department_id)
                    users = department.user_set.all()
                except Department.DoesNotExist:
                    return Response({'error': '找不到该部门'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # 管理员查看全公司统计，经理查看本部门统计
                if user.is_admin:
                    from users.models import User
                    users = User.objects.filter(is_active=True)
                else:
                    from users.models import User
                    users = User.objects.filter(department=user.department, is_active=True)
        else:
            # 普通员工只能查看自己的统计
            users = [user]
        
        statistics = {}
        for target_user in users:
            # 获取该用户在指定年份的请假统计
            leave_counts = LeaveApplication.objects.filter(
                user=target_user,
                start_date__year=year,
                status='approved'
            ).values('leave_type__name').annotate(total_days=Sum('days'))
            
            # 获取请假余额
            leave_balances = LeaveBalance.objects.filter(
                user=target_user,
                year=year
            )
            
            balance_data = {}
            for balance in leave_balances:
                balance_data[balance.leave_type.name] = {
                    'total': balance.total_days,
                    'used': balance.used_days,
                    'remaining': balance.remaining_days
                }
            
            # 获取该用户在指定年份的请假申请
            leave_records = LeaveApplication.objects.filter(
                user=target_user,
                start_date__year=year
            ).order_by('-created_at')
            
            records_data = LeaveApplicationSerializer(leave_records, many=True).data
            
            statistics[target_user.employee_id] = {
                'employee_id': target_user.employee_id,
                'name': f"{target_user.first_name} {target_user.last_name}" if target_user.first_name else target_user.username,
                'department': target_user.department.name if target_user.department else '',
                'position': target_user.position,
                'leave_counts': list(leave_counts),
                'leave_balances': balance_data,
                'leave_records': records_data
            }
        
        return Response({
            'statistics': statistics,
            'year': year
        })
