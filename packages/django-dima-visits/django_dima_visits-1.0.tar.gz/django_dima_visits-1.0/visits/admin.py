from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'ip_address', 'visit_time')
    search_fields = ('page_url', 'visit_time', 'ip_address')
    list_filter   = ('page_url', 'visit_time')
    
    