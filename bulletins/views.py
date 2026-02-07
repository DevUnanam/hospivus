from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Event, EventCategory, EventRegistration, SavedEvent


@method_decorator(login_required, name='dispatch')
class EventsListView(ListView):
    """Events list view with filtering and pagination"""
    
    model = Event
    template_name = "events.html"
    context_object_name = 'events'
    paginate_by = 6

    def get_queryset(self):
        queryset = Event.objects.filter(
            is_published=True,
            start_date__gte=timezone.now().date()
        ).select_related('category', 'location', 'created_by')

        # Filter by category
        category_filter = self.request.GET.get('category')
        if category_filter:
            queryset = queryset.filter(category__name__icontains=category_filter)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filter by online/in-person
        venue_type = self.request.GET.get('venue_type')
        if venue_type == 'online':
            queryset = queryset.filter(is_online=True)
        elif venue_type == 'in_person':
            queryset = queryset.filter(is_online=False)

        return queryset.order_by('start_date', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["categories"] = EventCategory.objects.all()
        context["event_types"] = Event.EVENT_TYPE_CHOICES
        
        # Get user's saved events
        if self.request.user.is_authenticated:
            context["saved_event_ids"] = list(
                SavedEvent.objects.filter(user=self.request.user)
                .values_list('event_id', flat=True)
            )
            context["registered_event_ids"] = list(
                EventRegistration.objects.filter(user=self.request.user)
                .values_list('event_id', flat=True)
            )
        else:
            context["saved_event_ids"] = []
            context["registered_event_ids"] = []
        
        # Add filter values to context
        context["current_category"] = self.request.GET.get('category', '')
        context["current_search"] = self.request.GET.get('search', '')
        context["current_event_type"] = self.request.GET.get('event_type', '')
        context["current_venue_type"] = self.request.GET.get('venue_type', '')
        
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    """Event detail view"""
    
    model = Event
    template_name = "event_detail.html"
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context["is_saved"] = SavedEvent.objects.filter(
                event=self.object, user=self.request.user
            ).exists()
            context["is_registered"] = EventRegistration.objects.filter(
                event=self.object, user=self.request.user
            ).exists()
        
        return context


class NonPatientRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only non-patients can access view"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type != 'PATIENT'


class EventCreateView(NonPatientRequiredMixin, CreateView):
    """Create new event - only for non-patients"""
    
    model = Event
    template_name = "event_form.html"
    fields = [
        'title', 'description', 'category', 'event_type', 'location',
        'is_online', 'online_platform', 'online_link', 'meeting_id',
        'start_date', 'end_date', 'start_time', 'end_time',
        'requires_registration', 'max_participants', 'registration_deadline',
        'registration_fee', 'image', 'is_featured'
    ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EventUpdateView(NonPatientRequiredMixin, UpdateView):
    """Update event - only for non-patients who created the event"""
    
    model = Event
    template_name = "event_form.html"
    fields = [
        'title', 'description', 'category', 'event_type', 'location',
        'is_online', 'online_platform', 'online_link', 'meeting_id',
        'start_date', 'end_date', 'start_time', 'end_time',
        'requires_registration', 'max_participants', 'registration_deadline',
        'registration_fee', 'image', 'is_featured'
    ]
    
    def test_func(self):
        obj = self.get_object()
        return (super().test_func() and 
                (obj.created_by == self.request.user or self.request.user.is_staff))


class EventDeleteView(NonPatientRequiredMixin, DeleteView):
    """Delete event - only for non-patients who created the event"""
    
    model = Event
    template_name = "event_confirm_delete.html"
    success_url = "/events/"
    
    def test_func(self):
        obj = self.get_object()
        return (super().test_func() and 
                (obj.created_by == self.request.user or self.request.user.is_staff))


@login_required
@require_POST
def register_for_event(request, event_id):
    """Register user for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if not event.requires_registration:
        return JsonResponse({'error': 'This event does not require registration'}, status=400)
    
    if not event.registration_open:
        return JsonResponse({'error': 'Registration is closed for this event'}, status=400)
    
    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        user=request.user
    )
    
    if created:
        messages.success(request, f'Successfully registered for {event.title}')
        return JsonResponse({'success': True, 'message': 'Registration successful'})
    else:
        return JsonResponse({'error': 'You are already registered for this event'}, status=400)


@login_required
@require_POST
def unregister_from_event(request, event_id):
    """Unregister user from an event"""
    event = get_object_or_404(Event, id=event_id)
    
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
        registration.delete()
        messages.success(request, f'Successfully unregistered from {event.title}')
        return JsonResponse({'success': True, 'message': 'Unregistration successful'})
    except EventRegistration.DoesNotExist:
        return JsonResponse({'error': 'You are not registered for this event'}, status=400)


@login_required
@require_POST
def save_event(request, event_id):
    """Save an event for later reference"""
    event = get_object_or_404(Event, id=event_id)
    
    saved_event, created = SavedEvent.objects.get_or_create(
        event=event,
        user=request.user
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Event saved successfully'})
    else:
        return JsonResponse({'error': 'Event is already saved'}, status=400)


@login_required
@require_POST
def unsave_event(request, event_id):
    """Remove an event from saved events"""
    event = get_object_or_404(Event, id=event_id)
    
    try:
        saved_event = SavedEvent.objects.get(event=event, user=request.user)
        saved_event.delete()
        return JsonResponse({'success': True, 'message': 'Event removed from saved'})
    except SavedEvent.DoesNotExist:
        return JsonResponse({'error': 'Event is not in your saved list'}, status=400)
