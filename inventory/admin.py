from django.contrib import admin
from .models import InventoryItem, Category, Project, Location  # Ensure Location is imported

admin.site.register(InventoryItem)
admin.site.register(Category)
admin.site.register(Project)

# Register the Location model with enhanced admin options
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name']  # Show the name of the location in the admin list view
    search_fields = ['name']  # Allow searching by location name
