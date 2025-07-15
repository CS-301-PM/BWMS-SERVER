from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.views import StockRequestViewSet
from inventory.views import DashboardStats
from inventory.views import StockItemViewSet

router = DefaultRouter()
router.register(r'stock-requests', StockRequestViewSet, basename='stockrequest')
router.register(r'stock-items', StockItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('api/dashboard/', DashboardStats.as_view()),
]