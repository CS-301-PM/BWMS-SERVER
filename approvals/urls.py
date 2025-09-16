from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'approvals', views.ApprovalViewSet, basename='approval')

urlpatterns = [
    path('', include(router.urls)),
]