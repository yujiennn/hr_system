from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'records', views.SalaryRecordViewSet)
router.register(r'structures', views.SalaryStructureViewSet)
router.register(r'items', views.SalaryItemViewSet)

urlpatterns = [
    path('my-salary/', views.MySalaryView.as_view(), name='my_salary'),
    path('my-records/', views.MySalaryView.as_view(), name='my_records'),
    path('payslips/', views.PayslipsView.as_view(), name='payslips'),
    path('payslip/<int:pk>/', views.PayslipView.as_view(), name='payslip'),
    path('export/', views.SalaryExportView.as_view(), name='salary_export'),
    path('statistics/', views.SalaryStatisticsView.as_view(), name='salary_statistics'),
    path('', include(router.urls)),
]
