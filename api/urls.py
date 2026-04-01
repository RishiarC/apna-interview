from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, QuizSessionViewSet, 
    TaskViewSet, JobRecommendationViewSet, AnalyticsViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'quizzes', QuizSessionViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'jobs', JobRecommendationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('analytics/', AnalyticsViewSet.as_view({'get': 'list'}), name='analytics'),
]
