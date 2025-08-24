from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views
from .face_views import (
    face_registration_view,
    face_recognition_view,
    face_status_view,
    delete_face_data_view
)

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'departments', views.DepartmentViewSet)

urlpatterns = [
    # JWT 认证
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 用户相关
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # 人脸识别相关
    path('face/register/', face_registration_view, name='face_register'),
    path('face/recognize/', face_recognition_view, name='face_recognize'),
    path('face/status/', face_status_view, name='face_status'),
    path('face/delete/', delete_face_data_view, name='face_delete'),
    
    # API 路由
    path('', include(router.urls)),
]
