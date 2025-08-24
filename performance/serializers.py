from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    PerformancePeriod, PerformanceTemplate, PerformanceIndicator,
    PerformanceGoal, PerformanceGoalDetail, PerformanceEvaluation,
    PerformanceEvaluationDetail
)
from users.serializers import UserSerializer

User = get_user_model()


class PerformancePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformancePeriod
        fields = '__all__'


class PerformanceIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceIndicator
        fields = '__all__'


class PerformanceTemplateSerializer(serializers.ModelSerializer):
    indicators = PerformanceIndicatorSerializer(many=True, read_only=True)
    
    class Meta:
        model = PerformanceTemplate
        fields = '__all__'


class PerformanceGoalDetailSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    indicator_description = serializers.CharField(source='indicator.description', read_only=True)
    max_score = serializers.IntegerField(source='indicator.max_score', read_only=True)
    
    class Meta:
        model = PerformanceGoalDetail
        fields = ['id', 'indicator', 'indicator_name', 'indicator_description', 
                 'target_value', 'weight', 'max_score']


class PerformanceGoalSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    period_name = serializers.CharField(source='period.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    approver_info = UserSerializer(source='approver', read_only=True)  # 完整的审批人信息
    approver_name = serializers.SerializerMethodField()  # 友好的审批人姓名
    details = PerformanceGoalDetailSerializer(many=True, read_only=True)
    
    def get_approver_name(self, obj):
        """获取审批人的友好显示名称"""
        if not obj.approver:
            return ''
        
        # 优先显示姓名，如果没有姓名则显示用户名
        if obj.approver.first_name and obj.approver.last_name:
            return f"{obj.approver.first_name} {obj.approver.last_name}"
        elif obj.approver.first_name:
            return obj.approver.first_name
        else:
            return obj.approver.username
    
    class Meta:
        model = PerformanceGoal
        fields = ['id', 'user', 'user_info', 'period', 'period_name', 
                 'template', 'template_name', 'status', 'approver', 'approver_info', 'approver_name',
                 'approval_note', 'approved_at', 'created_at', 'updated_at', 'details']
        read_only_fields = ['user', 'approver', 'approved_at']


class PerformanceEvaluationDetailSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    indicator_description = serializers.CharField(source='indicator.description', read_only=True)
    indicator_weight = serializers.FloatField(source='indicator.weight', read_only=True)
    max_score = serializers.IntegerField(source='indicator.max_score', read_only=True)
    
    class Meta:
        model = PerformanceEvaluationDetail
        fields = ['id', 'indicator', 'indicator_name', 'indicator_description',
                 'indicator_weight', 'max_score', 'self_score', 'self_comment',
                 'manager_score', 'manager_comment', 'final_score']
        read_only_fields = ['indicator']  # indicator字段设为只读


class PerformanceEvaluationSerializer(serializers.ModelSerializer):
    goal_info = PerformanceGoalSerializer(source='goal', read_only=True)
    evaluator_info = UserSerializer(source='evaluator', read_only=True)  # 完整的评估人信息
    evaluator_name = serializers.SerializerMethodField()  # 友好的评估人姓名
    details = PerformanceEvaluationDetailSerializer(many=True, read_only=True)
    
    # 计算字段
    user_name = serializers.CharField(source='goal.user.username', read_only=True)
    period_name = serializers.CharField(source='goal.period.name', read_only=True)
    template_name = serializers.CharField(source='goal.template.name', read_only=True)
    
    def get_evaluator_name(self, obj):
        """获取评估人的友好显示名称"""
        if not obj.evaluator:
            return ''
        
        # 优先显示姓名，如果没有姓名则显示用户名
        if obj.evaluator.first_name and obj.evaluator.last_name:
            return f"{obj.evaluator.first_name} {obj.evaluator.last_name}"
        elif obj.evaluator.first_name:            return obj.evaluator.first_name
        else:
            return obj.evaluator.username
    
    class Meta:
        model = PerformanceEvaluation
        fields = ['id', 'goal', 'goal_info', 'user_name', 'period_name', 'template_name',
                 'self_evaluation_score', 'self_evaluation_comment', 'self_evaluated_at',
                 'manager_evaluation_score', 'manager_evaluation_comment', 'manager_evaluated_at',
                 'evaluator', 'evaluator_info', 'evaluator_name', 'final_score', 'final_rating', 'status',
                 'created_at', 'updated_at', 'details']
        read_only_fields = ['evaluator', 'self_evaluated_at', 'manager_evaluated_at']


class PerformanceGoalCreateSerializer(serializers.ModelSerializer):
    """创建绩效目标的序列化器"""
    details = PerformanceGoalDetailSerializer(many=True)
    
    class Meta:
        model = PerformanceGoal
        fields = ['id', 'period', 'template', 'details', 'user', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'created_at']
    
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        
        # 创建绩效目标
        goal = PerformanceGoal.objects.create(user=user, **validated_data)
        
        # 创建目标明细
        for detail_data in details_data:
            PerformanceGoalDetail.objects.create(goal=goal, **detail_data)
        
        return goal


class SelfEvaluationDetailSerializer(serializers.ModelSerializer):
    """自评明细序列化器"""
    id = serializers.IntegerField()
    
    class Meta:
        model = PerformanceEvaluationDetail
        fields = ['id', 'self_score', 'self_comment']

class SelfEvaluationSerializer(serializers.ModelSerializer):
    """自评序列化器"""
    details = SelfEvaluationDetailSerializer(many=True)
    
    class Meta:
        model = PerformanceEvaluation
        fields = ['self_evaluation_score', 'self_evaluation_comment', 'details']
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        
        # 更新自评信息
        instance.self_evaluation_score = validated_data.get('self_evaluation_score', instance.self_evaluation_score)
        instance.self_evaluation_comment = validated_data.get('self_evaluation_comment', instance.self_evaluation_comment)
        instance.self_evaluated_at = timezone.now()
        instance.status = 'self_evaluated'
        
        # 自动分配评估人
        if not instance.evaluator:
            # 首先尝试找到用户的直接上级（部门经理）
            user_department = instance.goal.user.department
            if user_department:
                # 查找部门经理
                department_manager = User.objects.filter(
                    department=user_department,
                    user_type='manager'
                ).first()
                
                if department_manager:
                    instance.evaluator = department_manager
                else:
                    # 如果没有部门经理，分配给管理员
                    admin_user = User.objects.filter(user_type='admin').first()
                    if admin_user:
                        instance.evaluator = admin_user
        
        instance.save()
        
        # 更新明细自评
        for detail_data in details_data:
            detail_id = detail_data.get('id')
            if detail_id:
                try:
                    detail = instance.details.get(id=detail_id)
                    detail.self_score = detail_data.get('self_score', detail.self_score)
                    detail.self_comment = detail_data.get('self_comment', detail.self_comment)
                    detail.save()
                except PerformanceEvaluationDetail.DoesNotExist:
                    pass
        
        return instance
        
        return instance


class ManagerEvaluationDetailSerializer(serializers.ModelSerializer):
    """上级评估明细序列化器"""
    id = serializers.IntegerField()
    
    class Meta:
        model = PerformanceEvaluationDetail
        fields = ['id', 'manager_score', 'manager_comment']


class ManagerEvaluationSerializer(serializers.ModelSerializer):
    """上级评估序列化器"""
    details = ManagerEvaluationDetailSerializer(many=True)
    
    class Meta:
        model = PerformanceEvaluation
        fields = ['manager_evaluation_score', 'manager_evaluation_comment', 'final_score', 'final_rating', 'details']
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        
        # 更新上级评估信息（但不包括final_score，这个要通过计算得出）
        instance.manager_evaluation_score = validated_data.get('manager_evaluation_score', instance.manager_evaluation_score)
        instance.manager_evaluation_comment = validated_data.get('manager_evaluation_comment', instance.manager_evaluation_comment)
        instance.final_rating = validated_data.get('final_rating', instance.final_rating)
        instance.manager_evaluated_at = timezone.now()
        instance.evaluator = self.context['request'].user
        
        # 更新明细上级评分并计算加权总分
        total_weighted_score = 0
        total_weight = 0
        
        for detail_data in details_data:
            detail_id = detail_data.get('id')
            
            if detail_id:
                try:
                    detail = instance.details.get(id=detail_id)
                    detail.manager_score = detail_data.get('manager_score', detail.manager_score)
                    detail.manager_comment = detail_data.get('manager_comment', detail.manager_comment)
                    detail.final_score = detail_data.get('manager_score', detail.manager_score)
                    detail.save()
                    
                    # 计算加权总分
                    if detail.manager_score is not None:
                        weight = detail.indicator.weight
                        weighted_score = detail.manager_score * (weight / 100)
                        total_weighted_score += weighted_score
                        total_weight += weight
                        
                except PerformanceEvaluationDetail.DoesNotExist:
                    pass
        
        # 使用加权计算结果作为最终总分
        if total_weight > 0:
            instance.final_score = round(total_weighted_score, 2)
        else:
            # 如果没有明细或权重为0，则使用manager_evaluation_score作为备用
            instance.final_score = instance.manager_evaluation_score
            
        # 根据最终分数设置状态
        instance.status = 'finalized' if instance.final_score is not None else 'manager_evaluated'
        instance.save()
        
        return instance


class PerformanceStatisticsSerializer(serializers.Serializer):
    """绩效统计序列化器"""
    total_evaluations = serializers.IntegerField()
    completed_evaluations = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_score = serializers.FloatField()
    rating_distribution = serializers.DictField()
    department_stats = serializers.ListField()
