from django.contrib import admin
from .models import RegisAcc

class UserAdmin(admin.ModelAdmin):

    list_display = ('name', 'username', 'position', 'image_tag')  # Fields to show in the admin list
    search_fields = ('name', 'username', 'position')  # Enable search by these fields
    list_filter = ('position',)  # Filter by position in the sidebar
    ordering = ('name',)  # Default ordering by name
    
admin.site.register(RegisAcc,    UserAdmin)
