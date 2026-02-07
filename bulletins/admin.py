from django.contrib import admin
from .models.bulletins import Event, EventCategory, EventRegistration, SavedEvent


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'created_by', 'start_date', 'start_time', 
        'is_online', 'requires_registration', 'is_published', 'is_featured'
    ]
    list_filter = [
        'category', 'event_type', 'is_online', 'requires_registration', 
        'is_published', 'is_featured', 'start_date'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    ordering = ['-start_date', '-start_time']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'category', 'event_type', 'created_by')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time')
        }),
        ('Location', {
            'fields': ('location', 'is_online', 'online_platform', 'online_link', 'meeting_id', 'meeting_password')
        }),
        ('Registration', {
            'fields': ('requires_registration', 'max_participants', 'registration_deadline', 'registration_fee')
        }),
        ('Media & Status', {
            'fields': ('image', 'is_published', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Limit events shown to those created by the user if not superuser."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def save_model(self, request, obj, form, change):
        """Automatically set the created_by field to the current user."""
        if not change:  # Only on create
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'registration_date', 'attended']
    list_filter = ['attended', 'registration_date', 'event__category']
    search_fields = ['event__title', 'user__username', 'user__email']
    ordering = ['-registration_date']
    readonly_fields = ['registration_date']


@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'saved_date']
    list_filter = ['saved_date', 'event__category']
    search_fields = ['event__title', 'user__username', 'user__email']
    ordering = ['-saved_date']
    readonly_fields = ['saved_date']
