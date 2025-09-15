from django.contrib import admin
from .models import Approval

@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'stage', 'approver', 'status', 'date_updated')
    list_filter = ('stage', 'status', 'date_created')
    search_fields = ('request__id', 'approver__username', 'comment')
    readonly_fields = ('date_created', 'date_updated')