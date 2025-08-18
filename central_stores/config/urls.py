from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.views import DamageReportViewSet, DeliveryVerificationView, DepartmentRequestViewSet, RequestStatusView, StockMovementViewSet, StockRequestViewSet, SupplierDeliveryViewSet
from inventory.views import DashboardStats
from inventory.views import StockItemViewSet

router = DefaultRouter()
router.register(r'stock-requests', StockRequestViewSet, basename='stockrequest')
router.register(r'stock-items', StockItemViewSet)
router.register(r'stock-movements', StockMovementViewSet)  # Staff feature
router.register(r'damage-reports', DamageReportViewSet)    # Staff feature
router.register(r'department-requests', DepartmentRequestViewSet, basename='departmentrequest')
router.register(r'supplier-deliveries', SupplierDeliveryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('api/dashboard/', DashboardStats.as_view()),
    path('api/request-status/<int:pk>/', RequestStatusView.as_view()),
    path('api/verify-delivery/<int:pk>/', DeliveryVerificationView.as_view()),
]