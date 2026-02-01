from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from phonenumber_field.formfields import PhoneNumberField


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
        ]


class MultiUserRegistrationForm(UserCreationForm):
    """
    Extended user creation form that handles registration for all user types
    """
    # Common fields for all user types
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = PhoneNumberField(required=True)

    # Hidden fields for form processing
    user_type = forms.CharField(required=False, widget=forms.HiddenInput())

    # Address fields (common to all user types)
    address = forms.CharField(required=False, widget=forms.HiddenInput())
    city = forms.CharField(required=False, widget=forms.HiddenInput())
    state = forms.CharField(required=False, widget=forms.HiddenInput())
    postal_code = forms.CharField(required=False, widget=forms.HiddenInput())
    country = forms.CharField(required=False, widget=forms.HiddenInput())
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    # Individual Provider (formerly Physician) fields
    provider_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', '-- Select Provider Type --'),
            ('PHYSICIAN', 'Physician'),
            ('NURSE_PRACTITIONER', 'Nurse Practitioner'),
            ('PHYSICIAN_ASSISTANT', 'Physician Assistant'),
            ('THERAPIST', 'Therapist'),
            ('PHARMACIST', 'Pharmacist'),
            ('DENTIST', 'Dentist'),
            ('PSYCHOLOGIST', 'Psychologist'),
            ('OTHER', 'Other Healthcare Professional')
        ]
    )
    specialty = forms.CharField(required=False)
    license_number = forms.CharField(required=False)
    npi_number = forms.CharField(required=False)
    years_experience = forms.IntegerField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea())
    practice_name = forms.CharField(required=False)  # For location name
    insurance = forms.CharField(required=False)  # Individual provider insurance

    # Organization (formerly Healthcare Provider) fields
    organization_name = forms.CharField(required=False)
    organization_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', '-- Select Organization Type --'),
            ('HOSPITAL', 'Hospital'),
            ('CLINIC', 'Clinic'),
            ('URGENT_CARE', 'Urgent Care'),
            ('IMAGING_CENTER', 'Imaging Center'),
            ('LABORATORY', 'Laboratory'),
            ('PHARMACY', 'Pharmacy'),
            ('MENTAL_HEALTH_CENTER', 'Mental Health Center'),
            ('REHABILITATION_CENTER', 'Rehabilitation Center'),
            ('NURSING_HOME', 'Nursing Home'),
            ('MEDICAL_GROUP', 'Medical Group'),
            ('OTHER', 'Other')
        ]
    )
    tax_id = forms.CharField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea())

    # Multi-select fields for organizations
    services_offered = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('primary_care', 'Primary Care'),
            ('specialty_care', 'Specialty Care'),
            ('urgent_care', 'Urgent Care'),
            ('emergency', 'Emergency Services'),
            ('diagnostics', 'Diagnostic Services'),
            ('lab', 'Laboratory Services'),
            ('imaging', 'Imaging'),
            ('pharmacy', 'Pharmacy'),
            ('physical_therapy', 'Physical Therapy'),
            ('other', 'Other')
        ],
        widget=forms.CheckboxSelectMultiple()
    )

    insurance_accepted = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('medicare', 'Medicare'),
            ('medicaid', 'Medicaid'),
            ('blue_cross', 'Blue Cross Blue Shield'),
            ('aetna', 'Aetna'),
            ('cigna', 'Cigna'),
            ('humana', 'Humana'),
            ('united', 'UnitedHealthcare'),
            ('other', 'Other')
        ],
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'password1', 'password2'
        ]

    def clean(self):
        """
        Custom validation to ensure required fields are provided based on user type
        """
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type', self.data.get('user_type', ''))

        if user_type == 'physician':
            # Validate physician fields
            required_fields = ['specialty', 'license_number', 'years_experience']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for physicians.')

        elif user_type == 'provider':
            # Validate healthcare provider fields
            required_fields = ['organization_name', 'organization_type', 'tax_id']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for healthcare providers.')

        # Validate address fields if provided
        if cleaned_data.get('address'):
            required_address_fields = ['city', 'state', 'postal_code', 'country']
            for field in required_address_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'{field.replace("_", " ").title()} is required when address is provided.')

        return cleaned_data