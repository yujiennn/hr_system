from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.ReportCategoryViewSet)
router.register(r'templates', views.ReportTemplateViewSet)
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'schedules', views.ReportScheduleViewSet, basename='reportschedule')
router.register(r'logs', views.SystemLogViewSet, basename='systemlog')

urlpatterns = [
    path('generate/', views.ReportGenerationView.as_view(), name='report_generate'),
    path('statistics/', views.DataStatisticsView.as_view(), name='data_statistics'),
    path('', include(router.urls)),
]
