from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.db import transaction
from .models import User, Department
from .serializers import (
    UserSerializer, UserCreateSerializer, DepartmentSerializer,
    LoginSerializer, ChangePasswordSerializer, ProfileSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny]  # 临时允许无认证访问

    def get_permissions(self):
        # 临时注释认证检查，方便测试
        # if self.action in ['create', 'update', 'partial_update', 'destroy']:
        #     self.permission_classes = [permissions.IsAuthenticated]
        #     # 只有管理员可以修改部门
        #     if not self.request.user.is_admin:
        #         self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        # 所有操作都需要认证
        return [permissions.IsAuthenticated()]
    
    def check_write_permission(self):
        """检查写操作权限"""
        user = self.request.user
        # 管理员和经理可以进行写操作
        return getattr(user, 'is_admin', False) or getattr(user, 'is_manager', False)
    
    def create(self, request, *args, **kwargs):
        """创建用户 - 只有管理员和经理可以"""
        if not self.check_write_permission():
            return Response(
                {'detail': '只有管理员和部门经理可以创建用户'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新用户 - 只有管理员和经理可以"""
        if not self.check_write_permission():
            return Response(
                {'detail': '只有管理员和部门经理可以修改用户'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除用户 - 只有管理员可以"""
        user = self.request.user
        if not getattr(user, 'is_admin', False):
            return Response(
                {'detail': '只有管理员可以删除用户'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        elif user.is_manager:
            # 部门经理只能看到本部门的员工
            return User.objects.filter(department=user.department)
        else:
            # 普通员工只能看到自己
            return User.objects.filter(id=user.id)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        # 生成随机密码
        import random
        import string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(new_password)
        user.save()
        return Response({'message': '密码重置成功', 'password': new_password})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.is_active_employee = True
        user.save()
        return Response({'message': '用户已激活'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.is_active_employee = False
        user.save()
        return Response({'message': '用户已停用'})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            return Response({'message': '登出成功'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"ProfileView.put - User: {request.user.username}")
        logger.debug(f"ProfileView.put - Request data keys: {request.data.keys()}")
        logger.debug(f"ProfileView.put - Request files keys: {request.FILES.keys()}")
        
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            logger.debug(f"ProfileView.put - Serializer is valid, saving...")
            serializer.save()
            logger.debug(f"ProfileView.put - Data saved successfully")
            return Response(serializer.data)
        
        logger.error(f"ProfileView.put - Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"ProfileView.patch - User: {request.user.username}")
        logger.debug(f"ProfileView.patch - Request data keys: {request.data.keys()}")
        
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            logger.debug(f"ProfileView.patch - Serializer is valid, saving...")
            serializer.save()
            logger.debug(f"ProfileView.patch - Data saved successfully")
            return Response(serializer.data)
        
        logger.error(f"ProfileView.patch - Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': '密码修改成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
