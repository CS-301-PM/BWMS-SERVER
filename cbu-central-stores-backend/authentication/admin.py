from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'blockchain_address', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Blockchain Settings', {'fields': ('role', 'blockchain_address')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Blockchain Settings', {'fields': ('role', 'blockchain_address')}),
    )

admin.site.register(User, CustomUserAdmin)