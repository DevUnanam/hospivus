from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.http import Http404
import string

from .models import MedicalCondition


def conditions_index(request):
    """
    Display A-Z index of medical conditions.
    Shows all letters A-Z with counts of conditions for each letter.
    """
    # Get all letters A-Z
    alphabet = list(string.ascii_uppercase)
    
    # Get condition counts for each letter
    letter_counts = {}
    for letter in alphabet:
        count = MedicalCondition.objects.filter(name__istartswith=letter).count()
        letter_counts[letter] = count
    
    # Get departments for filter dropdown
    departments = MedicalCondition.objects.values_list('department', flat=True).distinct()
    department_choices = [
        (dept, dict(MedicalCondition.DEPARTMENTS).get(dept, dept))
        for dept in departments
    ]
    
    context = {
        'letter_counts': letter_counts,
        'alphabet': alphabet,
        'departments': department_choices,
        'total_conditions': MedicalCondition.objects.count(),
    }
    
    return render(request, 'health_tech/conditions_index.html', context)


def conditions_by_letter(request, letter):
    """
    Display all conditions starting with a specific letter.
    Includes pagination and department filtering.
    """
    letter = letter.upper()
    
    # Validate letter
    if letter not in string.ascii_uppercase:
        raise Http404("Invalid letter")
    
    # Get base queryset
    conditions = MedicalCondition.objects.filter(name__istartswith=letter)
    
    # Apply department filter if specified
    department_filter = request.GET.get('department')
    if department_filter:
        conditions = conditions.filter(department=department_filter)
    
    # Apply search filter if specified
    search_query = request.GET.get('search')
    if search_query:
        conditions = conditions.filter(
            Q(name__icontains=search_query) |
            Q(overview__icontains=search_query) |
            Q(symptoms__icontains=search_query)
        )
    
    # Order by name
    conditions = conditions.order_by('name')
    
    # Pagination
    paginator = Paginator(conditions, 20)  # Show 20 conditions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get departments for filter dropdown
    departments = MedicalCondition.objects.values_list('department', flat=True).distinct()
    department_choices = [
        (dept, dict(MedicalCondition.DEPARTMENTS).get(dept, dept))
        for dept in departments
    ]
    
    context = {
        'letter': letter,
        'page_obj': page_obj,
        'conditions': page_obj.object_list,
        'departments': department_choices,
        'current_department': department_filter,
        'search_query': search_query,
        'total_count': conditions.count() if not page_obj.paginator.count else page_obj.paginator.count,
    }
    
    return render(request, 'health_tech/conditions_by_letter.html', context)


class ConditionDetailView(DetailView):
    """
    Display detailed information about a single medical condition.
    """
    model = MedicalCondition
    template_name = 'health_tech/condition_detail.html'
    context_object_name = 'condition'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add related conditions
        context['related_conditions'] = self.object.get_related_conditions()
        
        # Add navigation info (previous/next alphabetically)
        current_letter = self.object.first_letter
        
        # Get previous condition
        try:
            context['previous_condition'] = MedicalCondition.objects.filter(
                name__lt=self.object.name
            ).order_by('-name').first()
        except MedicalCondition.DoesNotExist:
            context['previous_condition'] = None
            
        # Get next condition
        try:
            context['next_condition'] = MedicalCondition.objects.filter(
                name__gt=self.object.name
            ).order_by('name').first()
        except MedicalCondition.DoesNotExist:
            context['next_condition'] = None
            
        context['current_letter'] = current_letter
        
        return context


def search_conditions(request):
    """
    Search conditions across all fields.
    """
    query = request.GET.get('q', '').strip()
    conditions = []
    
    if query:
        conditions = MedicalCondition.objects.filter(
            Q(name__icontains=query) |
            Q(overview__icontains=query) |
            Q(symptoms__icontains=query) |
            Q(causes__icontains=query) |
            Q(treatments__icontains=query)
        ).order_by('name')
    
    # Pagination
    paginator = Paginator(conditions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'conditions': page_obj.object_list,
        'total_results': conditions.count() if conditions else 0,
    }
    
    return render(request, 'health_tech/search_results.html', context)