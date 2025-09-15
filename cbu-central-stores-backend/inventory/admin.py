from django.contrib import admin

from approvals import models
from .models import Product

class LowStockFilter(admin.SimpleListFilter):
    """A custom filter for the admin to show low stock items."""
    title = 'low stock status'  # A label for our filter
    parameter_name = 'low_stock'  # The URL parameter that will be used

    def lookups(self, request, model_admin):
        """Returns the list of filter options."""
        return (
            ('yes', 'Low Stock'),
            ('no', 'Adequate Stock'),
        )

    def queryset(self, request, queryset):
        """Applies the filter to the queryset based on the user's selection."""
        if self.value() == 'yes':
            # Filter for products where quantity <= threshold
            return queryset.filter(quantity__lte=models.F('low_stock_threshold'))
        if self.value() == 'no':
            # Filter for products where quantity > threshold
            return queryset.filter(quantity__gt=models.F('low_stock_threshold'))
        return queryset

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'low_stock_threshold', 'is_low_stock', 'date_updated')
    list_filter = ('category', LowStockFilter)  # Use our custom filter instead of the property
    search_fields = ('name', 'description')
    list_editable = ('quantity', 'low_stock_threshold')

    # We need to import models for the F() object in the filter
    from django.db import models