"""
Database Models for Users and Providers.
"""
from django.db import models
from django.contrib.auth.models import (
	AbstractBaseUser,
	BaseUserManager,
	PermissionsMixin,
)
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.uploader import destroy
from django.contrib.gis.db import models as gis_models
from django_countries.fields import CountryField


class UserManager(BaseUserManager):
	"""Manager for users."""

	def create_user(self, email, password=None, **extra_fields):
		"""Create, save and return a new user."""
		if not email:
			raise ValueError("User must have an email address")
		user = self.model(email=self.normalize_email(email), **extra_fields)
		user.set_password(password)
		user.save(using=self._db)

		return user

	def create_superuser(self, email, password):
		"""Create and return a new superuser."""
		user = self.create_user(email, password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)

		return user


class User(AbstractBaseUser, PermissionsMixin):
	"""User database model."""

	email = models.EmailField(
		max_length=255,
		unique=True,
		error_messages={"unique": "This email is already in use."},
	)
	first_name = models.CharField(max_length=255, db_index=True)
	last_name = models.CharField(max_length=255, db_index=True)
	phone_number = PhoneNumberField(
		unique=True,
		error_messages={"unique": "This phone number is already in use."},
		null=True,
		blank=True,
	)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	user_type = models.CharField(
		max_length=20,
		choices=[
			('INDIVIDUAL_PROVIDER', 'Individual Provider'),  # Doctors, Nurses, etc.
			('ORGANIZATION', 'Healthcare Organization'),     # Hospitals, Clinics, etc.
			('PATIENT', 'Patient'),
			('ADMIN', 'Administrator'),
		],
		default='PATIENT'
	)
	date_joined = models.DateTimeField(auto_now_add=True)

	objects = UserManager()

	USERNAME_FIELD = "email"

	def __str__(self):
		return self.email

	@property
	def full_name(self):
		return f"{self.first_name} {self.last_name}"


class PatientProfile(models.Model):
	"""Patient profile information."""

	user = models.OneToOneField(
		'accounts.User',
		on_delete=models.CASCADE,
		related_name='patient_profile'
	)
	date_of_birth = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=10, null=True, blank=True)
	profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


class IndividualProviderProfile(models.Model):
	"""Individual healthcare provider profile (doctors, nurses, therapists, etc.)"""

	user = models.OneToOneField(
		'accounts.User',
		on_delete=models.CASCADE,
		related_name='individual_provider_profile'
	)

	# Provider type and credentials
	provider_type = models.CharField(
		max_length=50,
		choices=[
			('PHYSICIAN', 'Physician'),
			('NURSE_PRACTITIONER', 'Nurse Practitioner'),
			('PHYSICIAN_ASSISTANT', 'Physician Assistant'),
			('THERAPIST', 'Therapist'),
			('PHARMACIST', 'Pharmacist'),
			('DENTIST', 'Dentist'),
			('PSYCHOLOGIST', 'Psychologist'),
			('OTHER', 'Other Healthcare Professional')
		],
		default='PHYSICIAN'
	)

	# Professional details
	specialty = models.CharField(max_length=255, blank=True, null=True)
	license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
	npi_number = models.CharField(max_length=50, blank=True, null=True)
	bio = models.TextField(blank=True, null=True)
	years_of_experience = models.PositiveIntegerField(default=0)
	education = models.TextField(blank=True, null=True)

	# Professional branding
	profile_picture = models.ImageField(upload_to='provider_pictures/', blank=True, null=True)
	logo = models.ImageField(upload_to='provider_logos/', blank=True, null=True)
	brand_color = models.CharField(max_length=20, blank=True, null=True, help_text="Hex color code")

	# Business details
	insurance_accepted = models.TextField(blank=True, null=True)
	services_offered = models.TextField(blank=True, null=True)

	# Payment details
	bank_name = models.CharField(max_length=255, blank=True, null=True)
	account_number = models.CharField(max_length=50, blank=True, null=True)
	routing_number = models.CharField(max_length=50, blank=True, null=True)

	# Verification
	is_verified = models.BooleanField(default=False)
	verification_date = models.DateTimeField(null=True, blank=True)

	appointment_types = models.JSONField(
		default=list,
		help_text="List of appointment types offered (IN_PERSON, VIDEO, PHONE)"
	)

	# Availability settings
	accepts_new_patients = models.BooleanField(default=True)

	# Online consultation settings
	video_consultation_link = models.URLField(
		blank=True,
		null=True,
		help_text="Default video consultation platform link"
	)

	# Booking settings
	advance_booking_days = models.IntegerField(
		default=90,
		help_text="How many days in advance patients can book"
	)
	minimum_notice_hours = models.IntegerField(
		default=24,
		help_text="Minimum hours notice required for booking"
	)

	# Add this method to the model
	def get_next_available_slot(self, appointment_type='IN_PERSON'):
		"""Get the next available appointment slot for this provider"""
		from appointments.models import OfficeHours, Appointment
		from datetime import datetime, timedelta
		from django.utils import timezone

		today = timezone.now().date()
		end_date = today + timedelta(days=self.advance_booking_days)

		# Get all office hours for this provider
		office_hours = OfficeHours.objects.filter(
			doctor=self,
			is_active=True
		).order_by('day_of_week', 'start_time')

		current_date = today
		while current_date <= end_date:
			weekday = current_date.weekday()

			# Get office hours for this day
			day_hours = office_hours.filter(day_of_week=weekday)

			for hours in day_hours:
				available_slots = hours.get_available_slots(current_date)
				if available_slots:
					return {
						'date': current_date,
						'time': available_slots[0]['start_time'],
						'location': hours.location
					}

			current_date += timedelta(days=1)

		return None

	def save(self, *args, **kwargs):
		if self.pk:
			old = IndividualProviderProfile.objects.get(pk=self.pk)
			if old.profile_picture and old.profile_picture != self.profile_picture:
				destroy(old.profile_picture.name)
			if old.logo and old.logo != self.logo:
				destroy(old.logo.name)

		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		if self.profile_picture:
			destroy(self.profile_picture.name)
		if self.logo:
			destroy(self.logo.name)
		super().delete(*args, **kwargs)

	def __str__(self):
		return f"{self.get_provider_type_display()} {self.user.full_name}"


class OrganizationProfile(models.Model):
	"""Healthcare organization profile (hospitals, clinics, pharmacies, etc.)"""

	user = models.OneToOneField(
		'accounts.User',
		on_delete=models.CASCADE,
		related_name='organization_profile'
	)

	# Organization details
	name = models.CharField(max_length=255)
	organization_type = models.CharField(
		max_length=50,
		choices=[
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
	description = models.TextField(blank=True, null=True)
	year_established = models.PositiveIntegerField(null=True, blank=True)

	# Contact information
	contact_email = models.EmailField(null=True, blank=True)
	contact_phone = PhoneNumberField(null=True, blank=True)
	website = models.URLField(blank=True, null=True)

	# Branding
	logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
	brand_color = models.CharField(max_length=20, blank=True, null=True, help_text="Hex color code")

	# Administrative details
	tax_id = models.CharField(max_length=50, blank=True, null=True)
	business_license = models.CharField(max_length=100, blank=True, null=True)

	# Services and insurance
	services_offered = models.TextField(blank=True, null=True)
	insurance_accepted = models.TextField(blank=True, null=True)

	# Payment details
	bank_name = models.CharField(max_length=255, blank=True, null=True)
	account_number = models.CharField(max_length=50, blank=True, null=True)
	routing_number = models.CharField(max_length=50, blank=True, null=True)

	# Verification
	is_verified = models.BooleanField(default=False)
	verification_date = models.DateTimeField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if self.pk:
			old = OrganizationProfile.objects.get(pk=self.pk)
			if old.logo and old.logo != self.logo:
				destroy(old.logo.name)
		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		if self.logo:
			destroy(self.logo.name)
		super().delete(*args, **kwargs)

	def __str__(self):
		return self.name


class ProviderLocation(models.Model):
	"""Physical location for any healthcare provider (individual or organization)"""

	# Generic foreign key to either individual provider or organization
	individual_provider = models.ForeignKey(
		IndividualProviderProfile,
		on_delete=models.CASCADE,
		related_name='locations',
		null=True,
		blank=True
	)
	organization = models.ForeignKey(
		OrganizationProfile,
		on_delete=models.CASCADE,
		related_name='locations',
		null=True,
		blank=True
	)

	# Location details
	name = models.CharField(max_length=255, null=True, blank=True)  # e.g., "Main Office", "North Campus"
	location_type = models.CharField(
		max_length=50,
		choices=[
			('MAIN', 'Main Location'),
			('BRANCH', 'Branch'),
			('SATELLITE', 'Satellite Office'),
			('SPECIALIZED', 'Specialized Unit'),
			('PRIVATE_PRACTICE', 'Private Practice')
		],
		default='MAIN'
	)

	# Address information
	address = models.CharField(max_length=255, null=True, blank=True)
	location = gis_models.PointField(null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	state = models.CharField(max_length=100, null=True, blank=True)
	zip_code = models.CharField(max_length=20, null=True, blank=True)
	country = CountryField(null=True, blank=True)

	# Contact details for this specific location
	phone = PhoneNumberField(blank=True, null=True)
	email = models.EmailField(blank=True, null=True)

	# Operating details
	hours_of_operation = models.TextField(null=True, blank=True)
	services_offered = models.TextField(null=True, blank=True)

	# Status
	is_active = models.BooleanField(default=True)
	is_primary = models.BooleanField(default=False)

	class Meta:
		constraints = [
			models.CheckConstraint(
				check=models.Q(individual_provider__isnull=False) | models.Q(organization__isnull=False),
				name='location_must_have_provider'
			),
			models.CheckConstraint(
				check=~(models.Q(individual_provider__isnull=False) & models.Q(organization__isnull=False)),
				name='location_cannot_have_both_providers'
			)
		]

	def __str__(self):
		provider_name = self.individual_provider.user.full_name if self.individual_provider else self.organization.name
		return f"{self.name or self.address} - {provider_name}"

	@property
	def provider(self):
		"""Return the associated provider (individual or organization)"""
		return self.individual_provider or self.organization


class UserLocation(models.Model):
	"""User's physical location information (for patients and other users)"""

	user = models.ForeignKey(
		'accounts.User',
		on_delete=models.CASCADE,
		related_name='user_locations'
	)
	address = models.CharField(max_length=255, null=True, blank=True)
	location = gis_models.PointField(null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	state = models.CharField(max_length=100, null=True, blank=True)
	zip_code = models.CharField(max_length=20, null=True, blank=True)
	country = CountryField(null=True, blank=True)
	is_primary = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.address}, {self.city}, {self.state}"


class ProviderAffiliation(models.Model):
	"""Represents an individual provider's affiliation with a healthcare organization"""

	individual_provider = models.ForeignKey(
		IndividualProviderProfile,
		on_delete=models.CASCADE,
		related_name='organization_affiliations'
	)
	organization = models.ForeignKey(
		OrganizationProfile,
		on_delete=models.CASCADE,
		related_name='individual_provider_affiliations'
	)
	location = models.ForeignKey(
		ProviderLocation,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='provider_affiliations'
	)

	# Affiliation details
	position = models.CharField(max_length=100, null=True, blank=True)  # e.g., "Staff Physician", "Department Head"
	department = models.CharField(max_length=100, null=True, blank=True)  # e.g., "Cardiology", "Emergency Medicine"
	employment_type = models.CharField(
		max_length=50,
		choices=[
			('EMPLOYEE', 'Employee'),
			('CONTRACTOR', 'Contractor'),
			('VOLUNTEER', 'Volunteer'),
			('CONSULTING', 'Consulting'),
			('PRIVILEGES', 'Hospital Privileges')
		],
		default='EMPLOYEE'
	)

	# Dates
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)
	is_primary = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)

	class Meta:
		unique_together = ['individual_provider', 'organization', 'location']

	def __str__(self):
		return f"{self.individual_provider} at {self.organization}"