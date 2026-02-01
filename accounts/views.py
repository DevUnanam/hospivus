from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout

from accounts.models.users import IndividualProviderProfile, OrganizationProfile, PatientProfile, ProviderLocation
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic import FormView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import logging
from django.db import transaction
from django_countries import countries
from django.shortcuts import redirect
from django.contrib.gis.geos import Point

from .forms import MultiUserRegistrationForm

logger = logging.getLogger(__name__)


class SignUpView(FormView):
    """View for multi-user type registration system"""

    redirect_authenticated_user = True
    template_name = "signup.html"
    form_class = MultiUserRegistrationForm
    success_url = reverse_lazy("core:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add countries for dropdown
        context["countries"] = list(countries)
        return context

    def get_form_kwargs(self):
        """Pass POST data to form even on GET requests when there are errors"""
        kwargs = super().get_form_kwargs()
        # If there's data in the session from a failed submission, use it
        if 'signup_form_data' in self.request.session:
            kwargs['data'] = self.request.session.pop('signup_form_data')
        return kwargs

    def form_valid(self, form):
        try:
            # Process the form data within a transaction
            with transaction.atomic():
                # Create the user
                user = form.save(commit=False)

                # Get user type from the form
                user_type = self.request.POST.get("user_type", "patient")

                # Convert to match the model's choices
                user_type_mapping = {
                    "patient": "PATIENT",
                    "physician": "INDIVIDUAL_PROVIDER",  # Updated mapping
                    "provider": "ORGANIZATION",  # Updated mapping
                }
                user.user_type = user_type_mapping.get(user_type, 'PATIENT')
                user.save()

                # Create the appropriate profile
                if user_type == 'physician':
                    self._create_individual_provider_profile(user, form.cleaned_data)
                elif user_type == 'provider':
                    self._create_organization_profile(user, form.cleaned_data)
                else:
                    self._create_patient_profile(user, form.cleaned_data)

                # Log user in
                login(self.request, user)

                # Set success message
                # messages.success(
                #     self.request,
                #     f"Welcome to UrbanMD, {user.first_name}! Your account has been created successfully."
                # )

                # Clear any stored form data
                if 'signup_form_data' in self.request.session:
                    del self.request.session['signup_form_data']

                return super().form_valid(form)

        except Exception as e:
            # Log the error
            logger.error(f"Error during user registration: {str(e)}")
            messages.error(
                self.request,
                "There was an error during registration. Please try again."
            )

            # Store form data in session to preserve it
            self.request.session['signup_form_data'] = self.request.POST

            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors"""
        # Store form data in session to preserve it
        self.request.session['signup_form_data'] = self.request.POST

        # Create a user-friendly error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                # Get field label if available
                field_label = form.fields.get(field, {}).label or field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")

        if error_messages:
            messages.error(
                self.request,
                "Please correct the following errors: " + " • ".join(error_messages)
            )

        # Log detailed errors for debugging
        logger.warning(f"Form validation failed: {form.errors}")

        return super().form_invalid(form)

    def _create_patient_profile(self, user, cleaned_data):
        """Create a patient profile"""
        # Create PatientProfile
        patient_profile = PatientProfile.objects.create(user=user)

    def _create_individual_provider_profile(self, user, cleaned_data):
        """Create an individual provider profile and location"""
        # Create IndividualProviderProfile
        individual_provider_profile = IndividualProviderProfile.objects.create(
            user=user,
            provider_type=cleaned_data.get('provider_type', 'PHYSICIAN'),  # Get from form
            specialty=cleaned_data.get('specialty', ''),
            license_number=cleaned_data.get('license_number', ''),
            npi_number=cleaned_data.get('npi_number', ''),
            years_of_experience=cleaned_data.get('years_experience', 0),
            insurance_accepted=cleaned_data.get('insurance', ''),
        )

        # Create provider location if address is provided
        address = cleaned_data.get('address')
        if address:
            location = ProviderLocation.objects.create(
                individual_provider=individual_provider_profile,
                name=cleaned_data.get('practice_name', 'Main Practice'),
                location_type='PRIVATE_PRACTICE',
                address=address,
                city=cleaned_data.get('city', ''),
                state=cleaned_data.get('state', ''),
                zip_code=cleaned_data.get('postal_code', ''),
                country=cleaned_data.get('country', ''),
                is_primary=True
            )
            # If we have latitude and longitude, save them
            if cleaned_data.get('latitude') and cleaned_data.get('longitude'):
                point = Point(
                    float(cleaned_data['longitude']),
                    float(cleaned_data['latitude']),
                    srid=4326
                )
                location.location = point
                location.save()

    def _create_organization_profile(self, user, cleaned_data):
        """Create an organization profile and location"""
        # Create OrganizationProfile
        logger.info(f'Creating organization profile for user {user.email}')
        logger.info(f'Organization type: {cleaned_data.get("organization_type", "")}')

        # Handle multiple selections for insurance and services
        insurance_options = cleaned_data.get('insurance_accepted', [])
        if isinstance(insurance_options, list):
            insurance_accepted_str = ','.join(insurance_options)
        else:
            insurance_accepted_str = insurance_options or ''

        services_offered = cleaned_data.get('services_offered', [])
        if isinstance(services_offered, list):
            services_offered_str = ','.join(services_offered)
        else:
            services_offered_str = services_offered or ''

        organization_profile = OrganizationProfile.objects.create(
            user=user,
            name=cleaned_data.get('organization_name', ''),
            organization_type=cleaned_data.get('organization_type', '').upper(),
            contact_email=user.email,
            contact_phone=user.phone_number,
            tax_id=cleaned_data.get('tax_id', ''),
            insurance_accepted=insurance_accepted_str,
            services_offered=services_offered_str,
        )

        # Create organization location if address is provided
        address = cleaned_data.get('address')
        if address:
            location = ProviderLocation.objects.create(
                organization=organization_profile,
                name="Main Location",
                location_type="MAIN",
                address=address,
                city=cleaned_data.get('city', ''),
                state=cleaned_data.get('state', ''),
                zip_code=cleaned_data.get('postal_code', ''),
                country=cleaned_data.get('country', ''),
                is_primary=True
            )
            if cleaned_data.get('latitude') and cleaned_data.get('longitude'):
                point = Point(
                    float(cleaned_data['longitude']),
                    float(cleaned_data['latitude']),
                    srid=4326
                )
                location.location = point
                location.save()

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            print(f"Field: {field}")
            for error in errors:
                print(f"  - {error}")

        return super().form_invalid(form)


class SignInView(LoginView):
	"""Sign in the user using html template"""
	template_name = 'signin.html'
	redirect_authenticated_user = True

	def dispatch(self, request, *args, **kwargs):
		if 'next' in request.GET:
			request.session['next'] = request.GET['next']
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		next_url = self.request.session.pop('next', None)
		return next_url or super().get_success_url()


@login_required
def signout(request):
	"""Sign out the user."""
	logout(request)
	return reverse('login_user')


class SettingsView(TemplateView):
	"""Settings view for the app"""
	template_name = "settings.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["user"] = self.request.user
		return context
