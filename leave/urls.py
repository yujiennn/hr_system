from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'applications', views.LeaveApplicationViewSet)
router.register(r'types', views.LeaveTypeViewSet)
router.register(r'balances', views.LeaveBalanceViewSet)

urlpatterns = [
    path('my-applications/', views.MyLeaveApplicationsView.as_view(), name='my_leave_applications'),
    path('approve/<int:pk>/', views.ApproveLeaveView.as_view(), name='approve_leave'),
    path('statistics/', views.LeaveStatisticsView.as_view(), name='leave_statistics'),
    path('', include(router.urls)),
]
