from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from .models import SystemConfig
from .serializers import (
    SystemConfigSerializer, 
    SystemConfigUpdateSerializer,
    EmailTestSerializer,
    SystemMaintenanceSerializer
)

class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置视图集"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        config_type = self.request.query_params.get('config_type')
        if config_type:
            queryset = queryset.filter(config_type=config_type)
        return queryset.order_by('config_type', 'key')
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新配置"""
        serializer = SystemConfigUpdateSerializer(data=request.data)
        if serializer.is_valid():
            configs = serializer.validated_data['configs']
            updated_configs = []
            
            for config_data in configs:
                config_id = config_data.get('id')
                if config_id:
                    try:
                        config = SystemConfig.objects.get(id=config_id)
                        for key, value in config_data.items():
                            if key != 'id' and hasattr(config, key):
                                setattr(config, key, value)
                        config.save()
                        updated_configs.append(config)
                    except SystemConfig.DoesNotExist:
                        continue
            
            # 清除缓存
            cache.clear()
            
            return Response({
                'message': f'成功更新 {len(updated_configs)} 个配置项',
                'updated_count': len(updated_configs)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按类型获取配置"""
        config_type = request.query_params.get('type')
        if not config_type:
            return Response({'error': '请提供配置类型'}, status=status.HTTP_400_BAD_REQUEST)
        
        configs = self.queryset.filter(config_type=config_type, is_active=True)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def test_email(self, request):
        """测试邮件配置"""
        serializer = EmailTestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # 获取邮件配置
                email_configs = SystemConfig.objects.filter(
                    config_type='email',
                    is_active=True
                ).values_list('key', 'value')
                
                config_dict = dict(email_configs)
                
                # 发送测试邮件
                send_mail(
                    subject=serializer.validated_data['subject'],
                    message=serializer.validated_data['message'],
                    from_email=config_dict.get('email_from', settings.DEFAULT_FROM_EMAIL),
                    recipient_list=[serializer.validated_data['recipient']],
                    fail_silently=False,
                )
                
                return Response({'message': '邮件发送成功'})
            except Exception as e:
                return Response(
                    {'error': f'邮件发送失败: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def maintenance(self, request):
        """系统维护操作"""
        serializer = SystemMaintenanceSerializer(data=request.data)
        if serializer.is_valid():
            action_type = serializer.validated_data['action']
            confirm = serializer.validated_data['confirm']
            
            if not confirm:
                return Response(
                    {'error': '请确认执行维护操作'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                if action_type == 'clear_cache':
                    cache.clear()
                    message = '缓存清理完成'
                elif action_type == 'clear_logs':
                    # 这里可以清理日志文件或数据库日志
                    message = '日志清理完成'
                elif action_type == 'restart_system':
                    # 这里可以触发系统重启逻辑
                    message = '系统重启请求已提交'
                else:
                    return Response(
                        {'error': '不支持的维护操作'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response({'message': message})
            except Exception as e:
                return Response(
                    {'error': f'维护操作失败: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def get_logo(self, request):
        """获取当前公司logo"""
        try:
            logo_config = SystemConfig.objects.get(
                key='company_logo',
                config_type='basic',
                is_active=True
            )
            return Response({
                'logo_url': logo_config.value,
                'description': logo_config.description
            })
        except SystemConfig.DoesNotExist:
            return Response({
                'logo_url': None,
                'message': '尚未设置公司logo'
            })
    
    @action(detail=False, methods=['post'])
    def set_logo(self, request):
        """设置公司logo"""
        logo_url = request.data.get('logo_url')
        if not logo_url:
            return Response({'error': 'logo_url参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 更新或创建logo配置
            logo_config, created = SystemConfig.objects.update_or_create(
                key='company_logo',
                config_type='basic',
                defaults={
                    'value': logo_url,
                    'description': '公司Logo',
                    'is_active': True,
                    'created_by': request.user
                }
            )
            
            action = '创建' if created else '更新'
            return Response({
                'message': f'公司Logo{action}成功',
                'logo_url': logo_url
            })
            
        except Exception as e:
            return Response(
                {'error': f'设置Logo失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def upload_logo(self, request):
        """上传公司logo文件"""
        if 'file' not in request.FILES:
            return Response({'error': '请选择要上传的文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response(
                {'error': '只支持上传 JPG、PNG、GIF、WebP 格式的图片'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证文件大小 (最大2MB)
        if file.size > 2 * 1024 * 1024:
            return Response(
                {'error': '文件大小不能超过2MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 生成唯一文件名
            ext = os.path.splitext(file.name)[1]
            filename = f"logo_{uuid.uuid4().hex}{ext}"
            
            # 保存文件到 media/logos/ 目录
            file_path = os.path.join('logos', filename)
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            
            # 构建完整的URL
            logo_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
            
            # 更新或创建logo配置
            logo_config, created = SystemConfig.objects.update_or_create(
                key='company_logo',
                config_type='basic',
                defaults={
                    'value': logo_url,
                    'description': '公司Logo',
                    'is_active': True,
                    'created_by': request.user
                }
            )
            
            return Response({
                'message': 'Logo上传成功',
                'logo_url': logo_url,
                'file_path': saved_path
            })
            
        except Exception as e:
            return Response(
                {'error': f'文件上传失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """文件上传接口"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '未提供文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 生成唯一文件名
            file_name = f"{uuid.uuid4().hex}_{file_obj.name}"
            # 保存文件
            file_path = default_storage.save(f"uploads/{file_name}", ContentFile(file_obj.read()))
            
            # 获取文件的绝对路径
            full_file_path = os.path.join(default_storage.location, file_path)
            
            return Response({
                'message': '文件上传成功',
                'file_path': file_path,
                'full_file_path': full_file_path
            })
        except Exception as e:
            return Response(
                {'error': f'文件上传失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
