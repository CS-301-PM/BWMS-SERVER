from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.BlockchainStatusView.as_view(), name='blockchain-status'),
    path('events/<int:request_id>/', views.BlockchainEventsView.as_view(), name='blockchain-events'),
]