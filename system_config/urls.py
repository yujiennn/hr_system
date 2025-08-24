from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .company_location_views import CompanyLocationViewSet

# 创建路由器实例
router = DefaultRouter()
router.register(r'configs', views.SystemConfigViewSet, basename='systemconfig')
router.register(r'company-locations', CompanyLocationViewSet, basename='companylocation')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
