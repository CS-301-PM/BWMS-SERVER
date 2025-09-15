from django.contrib import admin
from .models import DepartmentRequest

@admin.register(DepartmentRequest)
class DepartmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'requested_by', 'quantity_requested', 'priority', 'status', 'date_requested')
    list_filter = ('status', 'priority', 'date_requested')
    search_fields = ('product__name', 'requested_by__username', 'reason')
    readonly_fields = ('date_requested', 'date_updated')