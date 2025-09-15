from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_qr  # Import QR code views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('qr/scan/', views_qr.QRCodeScanView.as_view(), name='qr-scan'),
    path('products/<int:product_id>/qrcode/', views_qr.ProductQRCodeView.as_view(), name='product-qrcode'),
]