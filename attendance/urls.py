from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import face_views

router = DefaultRouter()
router.register(r'records', views.AttendanceRecordViewSet)
router.register(r'schedules', views.WorkScheduleViewSet)
router.register(r'exceptions', views.AttendanceExceptionViewSet)

urlpatterns = [
    path('clock/', views.ClockView.as_view(), name='clock'),
    path('clock-in/', views.ClockInView.as_view(), name='clock_in'),
    path('clock-out/', views.ClockOutView.as_view(), name='clock_out'),
    path('face-clock-in/', face_views.face_clock_in, name='face_clock_in'),
    path('face-clock-out/', face_views.face_clock_out, name='face_clock_out'),
    path('today-status/', views.TodayStatusView.as_view(), name='today_status'),
    path('monthly-stats/', views.MonthlyStatsView.as_view(), name='monthly_stats'),
    path('my-records/', views.MyRecordsView.as_view(), name='my_records'),
    path('statistics/', views.AttendanceStatisticsView.as_view(), name='attendance_statistics'),
    path('', include(router.urls)),
]
