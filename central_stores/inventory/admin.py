# inventory/admin.py
from django.contrib import admin
from .models import StockItem, StockRequest

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'location')
    search_fields = ('name', 'location')

@admin.register(StockRequest)
class StockRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'requester', 'status')
    list_filter = ('status',)