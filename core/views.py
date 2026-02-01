from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from accounts.models import IndividualProviderProfile


class LandingPageView(TemplateView):
    """Landing page"""

    template_name = "landing.html"

@method_decorator(login_required, name='dispatch')
class HealthView(TemplateView):
    """Health record view for the app"""

    template_name = "health_record.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class HelpView(TemplateView):
    """Help view for the app"""

    template_name = "help.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@login_required
@require_http_methods(["GET"])
def search_doctors_v2(request):
    """
    Search individual healthcare providers (keeping 'doctors' naming for backward compatibility)
    """
    # Get search parameters
    query = request.GET.get('query', '').strip()
    specialty = request.GET.get('specialty', '').strip()
    experience = request.GET.get('experience', '')
    insurance = request.GET.get('insurance', '').strip()
    availability = request.GET.get('availability', '')
    sort = request.GET.get('sort', 'relevance')
    provider_type = request.GET.get('provider_type', '')

    # Start with base queryset for individual providers
    doctors = IndividualProviderProfile.objects.select_related('user').prefetch_related(
        'organization_affiliations__organization',
        'organization_affiliations__location',
        'locations'
    ).filter(
        user__is_active=True,
        user__user_type='INDIVIDUAL_PROVIDER'
    )

    # Apply search query
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialty__icontains=query) |
            Q(bio__icontains=query) |
            Q(education__icontains=query) |
            Q(organization_affiliations__organization__name__icontains=query) |
            Q(organization_affiliations__department__icontains=query)
        ).distinct()

    # Apply provider type filter (new functionality)
    if provider_type:
        doctors = doctors.filter(provider_type=provider_type)

    # Apply specialty filter
    if specialty:
        doctors = doctors.filter(specialty__icontains=specialty)

    # Apply experience filter
    if experience:
        if experience == '0-5':
            doctors = doctors.filter(years_of_experience__lte=5)
        elif experience == '5-10':
            doctors = doctors.filter(years_of_experience__gte=5, years_of_experience__lte=10)
        elif experience == '10-15':
            doctors = doctors.filter(years_of_experience__gte=10, years_of_experience__lte=15)
        elif experience == '15+':
            doctors = doctors.filter(years_of_experience__gte=15)

    # Apply insurance filter
    if insurance:
        doctors = doctors.filter(insurance_accepted__icontains=insurance)

    # Apply availability filter (placeholder logic)
    if availability:
        if availability == 'today':
            doctors = doctors.filter(is_verified=True)
        elif availability == 'telehealth':
            # You might have a telehealth field in your model
            pass
        elif availability == 'new-patients':
            # You might have an accepting_new_patients field
            pass

    # Apply sorting
    if sort == 'experience':
        doctors = doctors.order_by('-years_of_experience')
    elif sort == 'rating':
        # Implement when you have ratings
        doctors = doctors.order_by('-is_verified', '-years_of_experience')
    elif sort == 'distance':
        # Implement when you have location data
        doctors = doctors.order_by('id')
    else:  # relevance
        doctors = doctors.order_by('-is_verified', '-years_of_experience')

    # Limit to 30 results
    doctors = doctors[:30]

    # Add mock data for ratings and reviews (replace with actual data later)
    import random
    for doctor in doctors:
        doctor.rating = round(random.uniform(4.5, 5.0), 1)
        doctor.reviews_count = random.randint(50, 300)
        doctor.available_today = random.choice([True, False])
        doctor.accepts_telehealth = random.choice([True, False])

    # Prepare the response
    if doctors:
        html = render_to_string('doctors/search_results.html', {
            'doctors': doctors,
            'count': len(doctors)
        })
        return JsonResponse({
            'success': True,
            'html': html,
            'count': len(doctors)
        })
    else:
        return JsonResponse({
            'success': False,
            'html': '',
            'count': 0
        })


"""
Views for the core app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Count, Prefetch
from datetime import datetime, timedelta, date
from django.utils import timezone

from accounts.models import User, IndividualProviderProfile, OrganizationProfile, ProviderLocation
from appointments.models import Appointment, OfficeHours
from giftshops.models import Product
from bulletins.models import Event


@login_required
def home(request):
    """
    Home view that displays different content based on user type
    """
    user = request.user
    context = {
        'user': user,
        'user_type': user.user_type,
    }

    if user.user_type == 'PATIENT':
        # Patient specific context
        context.update(get_patient_dashboard_context(user))
    elif user.user_type == 'INDIVIDUAL_PROVIDER':
        # Individual Provider (Doctor) specific context
        context.update(get_provider_dashboard_context(user))
    elif user.user_type == 'ORGANIZATION':
        # Organization specific context
        context.update(get_organization_dashboard_context(user))
    elif user.user_type == 'ADMIN':
        # Admin specific context
        context.update(get_admin_dashboard_context(user))

    return render(request, 'home2.html', context)


def get_patient_dashboard_context(user):
    """Get dashboard context for patient users"""
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=user,
        date__gte=timezone.now().date(),
        status__in=['SCHEDULED', 'CONFIRMED']
    ).select_related('doctor__user', 'location').order_by('date', 'start_time')[:3]

    # Get recommended products
    recommended_products = Product.objects.filter(
        is_active=True
    ).order_by('?')[:4]  # Random selection for now

    # Get upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now().date(),
        is_published=True
    ).order_by('start_date', 'start_time')[:3]

    # Get featured doctors
    featured_doctors = IndividualProviderProfile.objects.filter(
        is_verified=True,
        user__is_active=True
    ).select_related('user').order_by('?')[:4]  # Random selection

    # Recent messages (placeholder)
    recent_messages = []

    # Dashboard stats
    total_appointments = Appointment.objects.filter(patient=user).count()
    upcoming_appointments_count = Appointment.objects.filter(
        patient=user,
        date__gte=timezone.now().date(),
        status__in=['SCHEDULED', 'CONFIRMED']
    ).count()

    # Saved doctors (placeholder - you might want to add a favorites model)
    saved_doctors = 0

    return {
        'upcoming_appointments': upcoming_appointments,
        'dashboard_stats': {
            'total_appointments': total_appointments,
            'upcoming_appointments_count': upcoming_appointments_count,
            'saved_doctors': saved_doctors,
            'unread_messages': 0,  # Placeholder
        },
        'featured_doctors': featured_doctors,
        'recommended_products': recommended_products,
        'upcoming_events': upcoming_events,
        'recent_messages': recent_messages,
    }


def get_provider_dashboard_context(user):
    """Get dashboard context for provider users"""
    try:
        provider_profile = user.individual_provider_profile
    except IndividualProviderProfile.DoesNotExist:
        # Create a basic profile if it doesn't exist
        provider_profile = IndividualProviderProfile.objects.create(
            user=user,
            specialty='General Practice',  # Default
            is_verified=False
        )

    # Today's appointments
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        doctor=provider_profile,
        date=today,
        status__in=['SCHEDULED', 'CONFIRMED', 'IN_PROGRESS']
    ).select_related('patient', 'location').order_by('start_time')

    # This week's appointments count
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_appointments = Appointment.objects.filter(
        doctor=provider_profile,
        date__range=[week_start, week_end],
        status__in=['SCHEDULED', 'CONFIRMED', 'COMPLETED']
    ).count()

    # Recent messages (placeholder)
    recent_messages = []

    # Revenue stats (placeholder)
    monthly_revenue = 0
    pending_payments = 0

    return {
        'provider_profile': provider_profile,
        'todays_appointments': todays_appointments,
        'dashboard_stats': {
            'todays_appointments_count': todays_appointments.count(),
            'weekly_appointments_count': weekly_appointments,
            'total_patients': Appointment.objects.filter(
                doctor=provider_profile
            ).values('patient').distinct().count(),
            'new_patients_this_month': 0,  # To be implemented
            'monthly_revenue': monthly_revenue,
            'pending_payments': pending_payments,
            'rating': 4.8,  # Placeholder
            'reviews_count': 125,  # Placeholder
        },
        'recent_messages': recent_messages,
        'office_hours': OfficeHours.objects.filter(
            doctor=provider_profile
        ).order_by('day_of_week', 'start_time'),
    }


def get_organization_dashboard_context(user):
    """Get dashboard context for organization users"""
    try:
        org_profile = user.organization_profile
    except OrganizationProfile.DoesNotExist:
        # Create a basic profile if it doesn't exist
        org_profile = OrganizationProfile.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name} Organization"
        )

    # Get affiliated providers
    affiliated_providers = IndividualProviderProfile.objects.filter(
        organization_affiliations__organization=org_profile,
        organization_affiliations__is_active=True
    ).select_related('user').distinct()

    # Get organization locations
    locations = org_profile.locations.filter(is_active=True)

    # Today's appointments across all providers
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        doctor__in=affiliated_providers,
        date=today,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).count()

    # Monthly stats
    month_start = today.replace(day=1)
    monthly_appointments = Appointment.objects.filter(
        doctor__in=affiliated_providers,
        date__gte=month_start,
        status__in=['SCHEDULED', 'CONFIRMED', 'COMPLETED']
    ).count()

    # Recent activities (placeholder)
    recent_activities = []

    return {
        'organization_profile': org_profile,
        'affiliated_providers': affiliated_providers[:5],  # Show top 5
        'locations': locations,
        'dashboard_stats': {
            'total_providers': affiliated_providers.count(),
            'total_locations': locations.count(),
            'todays_appointments': todays_appointments,
            'monthly_appointments': monthly_appointments,
            'monthly_revenue': 0,  # To be implemented
            'patient_satisfaction': 4.6,  # Placeholder
            'active_patients': 0,  # To be implemented
            'new_patients_this_month': 0,  # To be implemented
        },
        'recent_activities': recent_activities,
    }


def get_admin_dashboard_context(user):
    """Get dashboard context for admin users"""
    # System-wide stats
    total_users = User.objects.filter(is_active=True).count()
    total_providers = IndividualProviderProfile.objects.filter(
        user__is_active=True
    ).count()
    total_organizations = OrganizationProfile.objects.filter(
        user__is_active=True
    ).count()
    total_patients = User.objects.filter(
        user_type='PATIENT',
        is_active=True
    ).count()

    # Today's activity
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        date=today
    ).count()

    new_users_today = User.objects.filter(
        date_joined__date=today
    ).count()

    # Pending verifications
    pending_provider_verifications = IndividualProviderProfile.objects.filter(
        is_verified=False
    ).count()

    pending_org_verifications = OrganizationProfile.objects.filter(
        is_verified=False
    ).count()

    return {
        'dashboard_stats': {
            'total_users': total_users,
            'total_providers': total_providers,
            'total_organizations': total_organizations,
            'total_patients': total_patients,
            'todays_appointments': todays_appointments,
            'new_users_today': new_users_today,
            'pending_provider_verifications': pending_provider_verifications,
            'pending_org_verifications': pending_org_verifications,
            'system_health': 'Operational',  # Placeholder
            'active_sessions': 0,  # To be implemented
        },
        'recent_activities': [],  # To be implemented
        'system_alerts': [],  # To be implemented
    }


@login_required
def search_doctors(request):
    """AJAX endpoint for searching doctors with availability filtering"""
    query = request.GET.get('query', '')
    specialty = request.GET.get('specialty', '')
    location = request.GET.get('location', '')
    insurance = request.GET.get('insurance', '')
    availability = request.GET.get('availability', '')
    experience = request.GET.get('experience', '')
    sort = request.GET.get('sort', 'relevance')

    # Base queryset
    doctors = IndividualProviderProfile.objects.filter(
        is_verified=True,
        user__is_active=True
    ).select_related('user').prefetch_related(
        Prefetch(
            'office_hours',
            queryset=OfficeHours.objects.filter(is_active=True)
        )
    )

    # Apply search query
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialty__icontains=query) |
            Q(sub_specialty__icontains=query)
        )

    # Apply filters
    if specialty:
        doctors = doctors.filter(specialty__icontains=specialty)

    if location:
        # Search by city, state, or zip
        doctors = doctors.filter(
            Q(locations__city__icontains=location) |
            Q(locations__state__icontains=location) |
            Q(locations__zip_code__icontains=location)
        ).distinct()

    if insurance:
        doctors = doctors.filter(insurance_accepted__icontains=insurance)

    if experience:
        if experience == '0-5':
            doctors = doctors.filter(years_of_experience__lte=5)
        elif experience == '5-10':
            doctors = doctors.filter(years_of_experience__range=(5, 10))
        elif experience == '10-15':
            doctors = doctors.filter(years_of_experience__range=(10, 15))
        elif experience == '15+':
            doctors = doctors.filter(years_of_experience__gte=15)

    # Apply availability filter based on actual office hours
    if availability:
        today = timezone.now().date()

        if availability == 'today':
            # Filter doctors who have office hours today and available slots
            weekday = today.weekday()
            doctors = doctors.filter(
                office_hours__day_of_week=weekday,
                office_hours__is_active=True
            ).distinct()

            # Further filter by those who have available slots
            available_doctors = []
            for doctor in doctors:
                has_availability = False
                for office_hour in doctor.office_hours.filter(day_of_week=weekday, is_active=True):
                    if office_hour.get_available_slots(today):
                        has_availability = True
                        break
                if has_availability:
                    available_doctors.append(doctor.id)

            doctors = doctors.filter(id__in=available_doctors)

        elif availability == 'this-week':
            # Filter doctors who have office hours this week
            week_start = today - timedelta(days=today.weekday())
            week_days = [week_start + timedelta(days=i) for i in range(7)]
            weekdays = [d.weekday() for d in week_days if d >= today]

            doctors = doctors.filter(
                office_hours__day_of_week__in=weekdays,
                office_hours__is_active=True
            ).distinct()

        elif availability == 'next-week':
            # Filter doctors who have office hours next week
            next_week_start = today + timedelta(days=(7 - today.weekday()))
            weekdays = list(range(7))  # All days of the week

            doctors = doctors.filter(
                office_hours__day_of_week__in=weekdays,
                office_hours__is_active=True
            ).distinct()

    # Apply sorting
    if sort == 'experience':
        doctors = doctors.order_by('-years_of_experience')
    elif sort == 'rating':
        # TODO: Implement when ratings are available
        doctors = doctors.order_by('-is_verified', '-years_of_experience')
    elif sort == 'distance':
        # TODO: Implement when location-based sorting is available
        doctors = doctors.order_by('id')
    else:  # relevance
        doctors = doctors.order_by('-is_verified', '-years_of_experience')

    # Limit results
    doctors = list(doctors[:30])

    # Add computed fields for display
    import random
    for doctor in doctors:
        doctor.rating = round(random.uniform(4.5, 5.0), 1)
        doctor.reviews_count = random.randint(50, 300)

        # Check actual availability for today
        today_weekday = today.weekday()
        doctor.available_today = doctor.office_hours.filter(
            day_of_week=today_weekday,
            is_active=True
        ).exists()

        # Check if doctor offers video consultations
        doctor.accepts_video = doctor.appointment_types and 'VIDEO' in doctor.appointment_types

    # Prepare the response
    if doctors:
        html = render_to_string('core/partials/doctor_search_results.html', {
            'doctors': doctors,
            'count': len(doctors)
        })
        return JsonResponse({
            'success': True,
            'html': html,
            'count': len(doctors)
        })
    else:
        return JsonResponse({
            'success': False,
            'html': '<div class="text-center py-12"><p class="text-gray-500">No doctors found matching your criteria.</p></div>',
            'count': 0
        })


@login_required
def refresh_dashboard_stats(request):
    """AJAX endpoint to refresh dashboard statistics"""
    user = request.user
    stats = {}

    if user.user_type == 'PATIENT':
        stats = get_patient_dashboard_context(user)['dashboard_stats']
    elif user.user_type == 'INDIVIDUAL_PROVIDER':
        stats = get_provider_dashboard_context(user)['dashboard_stats']
    elif user.user_type == 'ORGANIZATION':
        stats = get_organization_dashboard_context(user)['dashboard_stats']
    elif user.user_type == 'ADMIN':
        stats = get_admin_dashboard_context(user)['dashboard_stats']

    return JsonResponse({'success': True, 'stats': stats})


@login_required
def help(request):
    """Help and support page"""
    return render(request, 'core/help.html')


@login_required
def find_doctor(request):
    """Find doctor page"""
    # Get all active specialties for the filter
    specialties = IndividualProviderProfile.objects.filter(
        is_verified=True,
        user__is_active=True
    ).values_list('specialty', flat=True).distinct().order_by('specialty')

    context = {
        'specialties': [s for s in specialties if s],  # Filter out None/empty values
    }
    return render(request, 'core/find_doctor.html', context)