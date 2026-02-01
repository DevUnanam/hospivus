from django.contrib import admin
from django.utils.html import format_html
from .models import MedicalCondition


@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    """
    Admin interface for Medical Conditions.
    Provides comprehensive management with search, filters, and organized display.
    """
    list_display = [
        'name', 
        'first_letter_display', 
        'department_display_admin', 
        'has_image',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'department',
        'created_at',
        'updated_at',
        ('name', admin.EmptyFieldListFilter),  # Filter by first letter
    ]
    
    search_fields = [
        'name', 
        'overview', 
        'symptoms', 
        'causes', 
        'treatments'
    ]
    
    prepopulated_fields = {
        'slug': ('name',)
    }
    
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'first_letter_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 
                'slug', 
                'department',
                'image'
            )
        }),
        ('Content', {
            'fields': (
                'overview',
                'symptoms', 
                'causes', 
                'treatments'
            )
        }),
        ('Metadata', {
            'fields': (
                'first_letter_display',
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['name']
    
    actions = ['export_selected_conditions']
    
    def first_letter_display(self, obj):
        """Display the first letter of the condition name"""
        return obj.first_letter
    first_letter_display.short_description = 'Letter'
    first_letter_display.admin_order_field = 'name'
    
    def department_display_admin(self, obj):
        """Display formatted department name"""
        return obj.department_display
    department_display_admin.short_description = 'Department'
    department_display_admin.admin_order_field = 'department'
    
    def has_image(self, obj):
        """Show if condition has an associated image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 4px;" /> ✓',
                obj.image.url
            )
        return '✗'
    has_image.short_description = 'Image'
    has_image.allow_tags = True
    
    def export_selected_conditions(self, request, queryset):
        """Custom admin action to export selected conditions"""
        # This could be expanded to generate CSV/Excel exports
        count = queryset.count()
        self.message_user(
            request, 
            f'Selected {count} condition(s) for export.'
        )
    export_selected_conditions.short_description = "Export selected conditions"
    
    def get_queryset(self, request):
        """Optimize queries for admin list view"""
        return super().get_queryset(request).select_related().prefetch_related()
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)