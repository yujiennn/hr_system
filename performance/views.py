from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import (
    PerformancePeriod, PerformanceTemplate, PerformanceIndicator,
    PerformanceGoal, PerformanceGoalDetail, PerformanceEvaluation,
    PerformanceEvaluationDetail
)
from .serializers import (
    PerformancePeriodSerializer, PerformanceTemplateSerializer,
    PerformanceIndicatorSerializer, PerformanceGoalSerializer,
    PerformanceEvaluationSerializer, PerformanceGoalCreateSerializer,
    SelfEvaluationSerializer, ManagerEvaluationSerializer,
    PerformanceStatisticsSerializer
)
from users.models import User, Department


class PerformancePeriodViewSet(viewsets.ModelViewSet):
    """绩效周期视图集"""
    queryset = PerformancePeriod.objects.all()
    serializer_class = PerformancePeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # 只返回活跃的周期
            queryset = queryset.filter(is_active=True)
        return queryset


class PerformanceTemplateViewSet(viewsets.ModelViewSet):
    """绩效模板视图集"""
    queryset = PerformanceTemplate.objects.all()
    serializer_class = PerformanceTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # 只返回活跃的模板
            queryset = queryset.filter(is_active=True)
        return queryset


class PerformanceGoalViewSet(viewsets.ModelViewSet):
    """绩效目标视图集"""
    queryset = PerformanceGoal.objects.all()
    serializer_class = PerformanceGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # 根据用户角色过滤数据
        if user.user_type == 'admin':
            # 管理员可以查看所有
            pass
        elif user.user_type == 'manager':
            # 经理只能查看本部门
            queryset = queryset.filter(user__department=user.department)
        else:
            # 普通员工只能查看自己的
            queryset = queryset.filter(user=user)
          # 筛选参数
        period_id = self.request.query_params.get('period_id')
        if period_id:
            queryset = queryset.filter(period_id=period_id)
            
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PerformanceGoalCreateSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        """创建绩效目标，添加重复检查并自动分配审批人"""
        from django.db import IntegrityError
        
        # 检查是否已存在相同用户和周期的目标
        period_id = request.data.get('period')
        user = request.user
        
        if period_id:
            existing_goal = PerformanceGoal.objects.filter(
                user=user, 
                period_id=period_id
            ).first()
            
            if existing_goal:
                return Response({
                    'error': f'您已在该绩效周期中创建了目标，请勿重复创建。现有目标状态：{existing_goal.get_status_display()}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = super().create(request, *args, **kwargs)
            
            if response.status_code == 201 and 'id' in response.data:
                # 获取刚创建的目标
                goal_id = response.data['id']
                goal = PerformanceGoal.objects.get(id=goal_id)
                
                # 自动分配审批人
                approver = self._assign_approver(goal.user)
                if approver:
                    goal.approver = approver
                    goal.save()
                    
                    # 更新响应数据
                    serializer = self.get_serializer(goal)
                    response.data = serializer.data
            
            return response
            
        except IntegrityError as e:
            # 处理数据库唯一约束错误
            if 'user_id_period_id' in str(e):
                return Response({
                    'error': '您已在该绩效周期中创建了目标，请勿重复创建'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': f'创建失败：数据完整性错误 - {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    def _assign_approver(self, user):
        """自动分配审批人"""
        # 分配优先级：直属上级 > 部门经理 > 管理员
        approver = None
        
        # 1. 如果用户有部门，优先分配部门经理
        if user.department:
            managers = User.objects.filter(
                department=user.department,
                user_type='manager'
            )
            if managers.exists():
                approver = managers.first()
        
        # 2. 如果没有部门经理或用户没有部门，分配管理员
        if not approver:
            admin = User.objects.filter(user_type='admin').first()
            if admin:
                approver = admin
        
        return approver
    
    def _assign_evaluator(self, user):
        """自动分配评估人"""
        # 分配优先级：部门经理 > 管理员
        evaluator = None
        
        # 1. 如果用户有部门，优先分配部门经理
        if user.department:
            managers = User.objects.filter(
                department=user.department,
                user_type='manager'
            )
            if managers.exists():
                evaluator = managers.first()
        
        # 2. 如果没有部门经理或用户没有部门，分配管理员
        if not evaluator:
            admin = User.objects.filter(user_type='admin').first()
            if admin:
                evaluator = admin
        
        return evaluator
    
    @action(detail=False, methods=['get'])
    def my_goals(self, request):
        """获取我的绩效目标"""
        goals = PerformanceGoal.objects.filter(user=request.user)
        
        # 筛选参数
        period_id = request.query_params.get('period_id')
        if period_id:
            goals = goals.filter(period_id=period_id)
        
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交绩效目标"""
        goal = self.get_object()
        
        # 检查权限
        if goal.user != request.user:
            return Response({'error': '无权操作此目标'}, status=status.HTTP_403_FORBIDDEN)
        
        if goal.status != 'draft':
            return Response({'error': '只有草稿状态的目标可以提交'}, status=status.HTTP_400_BAD_REQUEST)
        
        goal.status = 'submitted'
        goal.save()
          # 创建对应的评估记录
        evaluation, created = PerformanceEvaluation.objects.get_or_create(goal=goal)
        if created:
            # 自动分配评估人
            evaluator = self._assign_evaluator(goal.user)
            if evaluator:
                evaluation.evaluator = evaluator
                evaluation.save()
            
            # 为每个指标创建评估明细
            for detail in goal.details.all():
                PerformanceEvaluationDetail.objects.create(
                    evaluation=evaluation,
                    indicator=detail.indicator
                )
        
        return Response({'message': '目标提交成功'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批绩效目标"""
        goal = self.get_object()
        
        # 检查权限
        user = request.user
        
        # 权限检查：
        # 1. 管理员可以审批任何人的目标
        # 2. 经理可以审批同部门员工的目标
        # 3. 财务部员工可以审批任何人的目标（财务职能）
        can_approve = (
            user.is_admin or 
            (user.is_manager and user.department == goal.user.department) or
            user.is_finance_department
        )
        
        if not can_approve:
            return Response({'error': '无权限审批此目标'}, status=status.HTTP_403_FORBIDDEN)
        
        if goal.status != 'submitted':
            return Response({'error': '只有已提交的目标可以审批'}, status=status.HTTP_400_BAD_REQUEST)
        
        approval_status = request.data.get('status')  # 'approved' 或 'rejected'
        approval_note = request.data.get('note', '')
        
        if approval_status not in ['approved', 'rejected']:
            return Response({'error': '审批状态无效'}, status=status.HTTP_400_BAD_REQUEST)
        
        goal.status = approval_status
        goal.approver = user
        goal.approval_note = approval_note
        goal.approved_at = timezone.now()
        goal.save()
        
        return Response({'message': f'目标{approval_status}成功'})


class PerformanceEvaluationViewSet(viewsets.ModelViewSet):
    """绩效评估视图集"""
    queryset = PerformanceEvaluation.objects.all()
    serializer_class = PerformanceEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """创建绩效评估，自动分配评估人"""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == 201:
            # 获取刚创建的评估
            evaluation_id = response.data['id']
            evaluation = PerformanceEvaluation.objects.get(id=evaluation_id)
            
            # 自动分配评估人（设置为被评估用户的部门经理或管理员）
            user_being_evaluated = evaluation.goal.user
            
            # 寻找评估人优先级：部门经理 > 管理员
            evaluator = None
            
            # 1. 优先分配部门经理
            if user_being_evaluated.department:
                managers = User.objects.filter(
                    department=user_being_evaluated.department,
                    user_type='manager'
                ).first()
                if managers:
                    evaluator = managers
            
            # 2. 如果没有部门经理，分配管理员
            if not evaluator:
                admin = User.objects.filter(user_type='admin').first()
                if admin:
                    evaluator = admin
            
            # 3. 分配评估人
            if evaluator:
                evaluation.evaluator = evaluator
                evaluation.save()
                
                # 更新响应数据
                serializer = self.get_serializer(evaluation)
                response.data = serializer.data
        
        return response
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # 根据用户角色过滤数据
        if user.user_type == 'admin':
            # 管理员可以查看所有
            pass
        elif user.user_type == 'manager':
            # 经理可以查看本部门员工的评估，以及自己作为评估人的评估
            if user.department:
                queryset = queryset.filter(
                    Q(goal__user__department=user.department) | Q(evaluator=user)
                )
            else:
                # 如果经理没有部门，只能查看自己作为评估人的评估或自己的评估
                queryset = queryset.filter(Q(evaluator=user) | Q(goal__user=user))
        else:
            # 普通员工只能查看自己的
            queryset = queryset.filter(goal__user=user)
        
        # 筛选参数
        period_id = self.request.query_params.get('period_id')
        if period_id:
            queryset = queryset.filter(goal__period_id=period_id)
            
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_evaluations(self, request):
        """获取我的绩效评估"""
        evaluations = PerformanceEvaluation.objects.filter(goal__user=request.user)
        
        # 筛选参数
        period_id = request.query_params.get('period_id')
        if period_id:
            evaluations = evaluations.filter(goal__period_id=period_id)
        
        # 按更新时间降序排列，确保最新的在前面
        evaluations = evaluations.order_by('-updated_at')
        
        serializer = self.get_serializer(evaluations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def self_evaluate(self, request, pk=None):
        """自评"""
        evaluation = self.get_object()
        
        # 检查权限 - 只有评估所属的员工本人才能自评
        if evaluation.goal.user != request.user:
            return Response({
                'error': '无权操作此评估',
                'detail': f'此评估属于用户 {evaluation.goal.user.username}，当前登录用户为 {request.user.username}'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if evaluation.status not in ['draft', 'self_evaluated']:
            return Response({'error': f'当前状态({evaluation.status})不允许自评，只有草稿或自评完成状态可以修改'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SelfEvaluationSerializer(evaluation, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '自评提交成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def manager_evaluate(self, request, pk=None):
        """上级评估"""
        evaluation = self.get_object()
        
        # 检查权限 - 只有管理员和经理可以评估
        user = request.user
        evaluated_user = evaluation.goal.user
        
        # 调试日志
        print(f"[DEBUG] manager_evaluate: user={user.username}, user_type={user.user_type}, evaluated_user={evaluated_user.username}")
        
        # 权限检查：管理员或该部门的经理
        if user.user_type == 'admin':
            # 管理员可以评估任何人
            pass
        elif user.user_type == 'manager':
            # 经理只能评估自己部门的员工
            if evaluated_user.department != user.department:
                return Response({'error': '无权限评估其他部门员工'}, status=status.HTTP_403_FORBIDDEN)
        else:
            print(f"[DEBUG] 权限拒绝: user_type={user.user_type} 不是 admin 或 manager")
            return Response({'error': f'无权限评估 (user_type={user.user_type})'}, status=status.HTTP_403_FORBIDDEN)
        
        if evaluation.status not in ['self_evaluated', 'manager_evaluated']:
            return Response({'error': '当前状态不允许上级评估'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ManagerEvaluationSerializer(evaluation, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '评估提交成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """绩效统计"""
        # 获取查询参数
        period_id = request.query_params.get('period_id')
        department_id = request.query_params.get('department_id')
        
        # 构建查询条件
        queryset = PerformanceEvaluation.objects.all()
        if period_id:
            queryset = queryset.filter(goal__period_id=period_id)
        if department_id:
            queryset = queryset.filter(goal__user__department_id=department_id)
        
        # 根据用户权限过滤
        user = request.user
        if user.user_type == 'manager':
            # 经理只能查看本部门统计
            queryset = queryset.filter(goal__user__department=user.department)
        
        # 统计数据
        total_evaluations = queryset.count()
        completed_evaluations = queryset.filter(status='finalized').count()
        completion_rate = (completed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0
        
        # 平均分数
        avg_score = queryset.filter(final_score__isnull=False).aggregate(avg=Avg('final_score'))['avg'] or 0
        
        # 等级分布
        rating_distribution = {}
        for choice in PerformanceEvaluation.RATING_CHOICES:
            rating_code, rating_label = choice
            count = queryset.filter(final_rating=rating_code).count()
            rating_distribution[rating_label] = count
          # 部门统计
        department_stats = []
        if user.user_type == 'admin':
            from users.models import Department
            departments = Department.objects.all()
            for dept in departments:
                dept_evaluations = queryset.filter(goal__user__department=dept)
                if dept_evaluations.exists():
                    dept_total = dept_evaluations.count()
                    dept_completed = dept_evaluations.filter(status='finalized').count()
                    dept_avg_score = dept_evaluations.filter(final_score__isnull=False).aggregate(avg=Avg('final_score'))['avg'] or 0
                    
                    department_stats.append({
                        'department': dept.name,
                        'total_evaluations': dept_total,
                        'completed_evaluations': dept_completed,
                        'completion_rate': (dept_completed / dept_total * 100) if dept_total > 0 else 0,
                        'average_score': round(dept_avg_score, 2)
                    })
        
        data = {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'completion_rate': round(completion_rate, 2),
            'average_score': round(avg_score, 2),
            'rating_distribution': rating_distribution,
            'department_stats': department_stats
        }
        
        return Response(data)
