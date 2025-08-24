from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PerformancePeriodViewSet,
    PerformanceTemplateViewSet,
    PerformanceGoalViewSet,
    PerformanceEvaluationViewSet
)

router = DefaultRouter()
router.register(r'periods', PerformancePeriodViewSet)
router.register(r'templates', PerformanceTemplateViewSet)
router.register(r'goals', PerformanceGoalViewSet)
router.register(r'evaluations', PerformanceEvaluationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
