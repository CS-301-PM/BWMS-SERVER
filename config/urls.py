from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from utils.api_views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/inventory/', include('inventory.urls')),
    path('api/requests/', include('procurement_requests.urls')),
    path('api/approvals/', include('approvals.urls')),
    path('api/blockchain/', include('blockchain.urls')),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
]