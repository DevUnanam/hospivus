"""
Management command to populate the database with sample data for development and testing.

This command creates:
- Event categories
- Healthcare organizations (20)
- Individual providers (50) 
- Events (30) with proper associations
"""

import random
from datetime import date, datetime, timedelta, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models.users import (
    IndividualProviderProfile, 
    OrganizationProfile, 
    ProviderLocation
)
from bulletins.models.bulletins import Event, EventCategory, EventRegistration

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data for events, organizations, and providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Event.objects.all().delete()
            EventCategory.objects.all().delete()
            ProviderLocation.objects.all().delete()
            IndividualProviderProfile.objects.all().delete()
            OrganizationProfile.objects.all().delete()
            User.objects.filter(user_type__in=['INDIVIDUAL_PROVIDER', 'ORGANIZATION']).delete()

        self.stdout.write('Creating event categories...')
        self.create_event_categories()
        
        self.stdout.write('Creating healthcare organizations...')
        self.create_organizations()
        
        self.stdout.write('Creating individual providers...')
        self.create_individual_providers()
        
        self.stdout.write('Creating events...')
        self.create_events()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated database with sample data!\n'
                f'- Event Categories: {EventCategory.objects.count()}\n'
                f'- Organizations: {OrganizationProfile.objects.count()}\n' 
                f'- Individual Providers: {IndividualProviderProfile.objects.count()}\n'
                f'- Events: {Event.objects.count()}'
            )
        )

    def create_event_categories(self):
        """Create event categories with icons and colors."""
        categories_data = [
            {
                'name': 'Health Camps',
                'description': 'Free health screening and check-up camps',
                'icon': '🏕️',
                'color': 'green'
            },
            {
                'name': 'Workshops',
                'description': 'Educational workshops and training sessions',
                'icon': '📚',
                'color': 'blue'
            },
            {
                'name': 'Seminars',
                'description': 'Medical seminars and conferences',
                'icon': '🎯',
                'color': 'purple'
            },
            {
                'name': 'Webinars',
                'description': 'Online educational sessions',
                'icon': '💻',
                'color': 'indigo'
            },
            {
                'name': 'Free Consultations',
                'description': 'Free medical consultations and advice',
                'icon': '🩺',
                'color': 'red'
            },
            {
                'name': 'Health Screenings',
                'description': 'Preventive health screening programs',
                'icon': '🔍',
                'color': 'yellow'
            },
            {
                'name': 'Support Groups',
                'description': 'Patient and family support group meetings',
                'icon': '🤝',
                'color': 'pink'
            },
            {
                'name': 'Vaccination Drives',
                'description': 'Community vaccination programs',
                'icon': '💉',
                'color': 'orange'
            }
        ]

        for cat_data in categories_data:
            category, created = EventCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')

    def create_organizations(self):
        """Create 20 healthcare organizations with locations."""
        
        organizations_data = [
            {
                'name': 'Idaho Teaching Hospital',
                'type': 'HOSPITAL',
                'city': 'Boise',
                'state': 'Idaho',
                'specialties': ['Internal Medicine', 'Surgery', 'Pediatrics']
            },
            {
                'name': 'Mountain View Medical Center',
                'type': 'CLINIC',
                'city': 'Salt Lake City',
                'state': 'Utah',
                'specialties': ['Cardiology', 'Orthopedics', 'Emergency Medicine']
            },
            {
                'name': 'Pacific Northwest Clinic',
                'type': 'CLINIC',
                'city': 'Seattle',
                'state': 'Washington',
                'specialties': ['Family Medicine', 'Dermatology', 'Mental Health']
            },
            {
                'name': 'Valley Health Systems',
                'type': 'MEDICAL_GROUP',
                'city': 'Phoenix',
                'state': 'Arizona',
                'specialties': ['Oncology', 'Neurology', 'Radiology']
            },
            {
                'name': 'Community Care Hospital',
                'type': 'HOSPITAL',
                'city': 'Denver',
                'state': 'Colorado',
                'specialties': ['Emergency Medicine', 'Surgery', 'Obstetrics']
            },
            {
                'name': 'Metropolitan Medical Group',
                'type': 'MEDICAL_GROUP',
                'city': 'Las Vegas',
                'state': 'Nevada',
                'specialties': ['Internal Medicine', 'Endocrinology', 'Nephrology']
            },
            {
                'name': 'Regional Cancer Center',
                'type': 'OTHER',
                'city': 'Portland',
                'state': 'Oregon',
                'specialties': ['Oncology', 'Hematology', 'Radiation Oncology']
            },
            {
                'name': 'Sunrise Healthcare Network',
                'type': 'MEDICAL_GROUP',
                'city': 'Albuquerque',
                'state': 'New Mexico',
                'specialties': ['Family Medicine', 'Pediatrics', 'Women\'s Health']
            },
            {
                'name': 'Central Valley Clinic',
                'type': 'CLINIC',
                'city': 'Fresno',
                'state': 'California',
                'specialties': ['Primary Care', 'Diabetes Care', 'Preventive Medicine']
            },
            {
                'name': 'Desert Medical Institute',
                'type': 'CLINIC',
                'city': 'Tucson',
                'state': 'Arizona',
                'specialties': ['Cardiology', 'Pulmonology', 'Critical Care']
            },
            {
                'name': 'Northern California Medical Group',
                'type': 'MEDICAL_GROUP',
                'city': 'Sacramento',
                'state': 'California',
                'specialties': ['Family Medicine', 'Geriatrics', 'Mental Health']
            },
            {
                'name': 'Rocky Mountain Hospital',
                'type': 'HOSPITAL',
                'city': 'Colorado Springs',
                'state': 'Colorado',
                'specialties': ['Emergency Medicine', 'Trauma Surgery', 'Intensive Care']
            },
            {
                'name': 'Coastal Health Partners',
                'type': 'MEDICAL_GROUP',
                'city': 'San Diego',
                'state': 'California',
                'specialties': ['Orthopedics', 'Sports Medicine', 'Physical Therapy']
            },
            {
                'name': 'Intermountain Wellness Center',
                'type': 'OTHER',
                'city': 'Provo',
                'state': 'Utah',
                'specialties': ['Preventive Care', 'Nutrition', 'Wellness Programs']
            },
            {
                'name': 'Southwest Regional Medical',
                'type': 'HOSPITAL',
                'city': 'El Paso',
                'state': 'Texas',
                'specialties': ['Emergency Medicine', 'Internal Medicine', 'Surgery']
            },
            {
                'name': 'Urban Health Collective',
                'type': 'OTHER',
                'city': 'Los Angeles',
                'state': 'California',
                'specialties': ['Community Health', 'Public Health', 'Social Medicine']
            },
            {
                'name': 'Innovation Medical Center',
                'type': 'CLINIC',
                'city': 'Austin',
                'state': 'Texas',
                'specialties': ['Telemedicine', 'Digital Health', 'Research']
            },
            {
                'name': 'Heritage Family Clinic',
                'type': 'CLINIC',
                'city': 'Oklahoma City',
                'state': 'Oklahoma',
                'specialties': ['Family Medicine', 'Pediatrics', 'Women\'s Health']
            },
            {
                'name': 'Advanced Cardiac Institute',
                'type': 'OTHER',
                'city': 'Dallas',
                'state': 'Texas',
                'specialties': ['Cardiology', 'Cardiac Surgery', 'Interventional Cardiology']
            },
            {
                'name': 'Comprehensive Care Associates',
                'type': 'MEDICAL_GROUP',
                'city': 'Kansas City',
                'state': 'Missouri',
                'specialties': ['Internal Medicine', 'Family Medicine', 'Chronic Care']
            }
        ]

        created_orgs = []
        
        for org_data in organizations_data:
            # Create organization user account
            org_name_clean = org_data['name'].lower().replace(' ', '').replace("'", '')
            email = f"admin@{org_name_clean}.com"
            
            org_user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': org_data['name'],
                    'last_name': 'Admin',
                    'user_type': 'ORGANIZATION',
                }
            )
            
            if created:
                org_user.set_password('testpass123')
                org_user.save()

            # Create organization profile
            org_profile, profile_created = OrganizationProfile.objects.get_or_create(
                user=org_user,
                defaults={
                    'name': org_data['name'],
                    'organization_type': org_data['type'],
                    'services_offered': ', '.join(org_data['specialties']),
                    'description': f"{org_data['name']} is a leading healthcare provider specializing in {', '.join(org_data['specialties'][:2])}."
                }
            )

            # Create main location
            location, loc_created = ProviderLocation.objects.get_or_create(
                organization=org_profile,
                name=f"{org_data['name']} - Main Campus",
                defaults={
                    'location_type': 'MAIN',
                    'address': f"123 Healthcare Blvd",
                    'city': org_data['city'],
                    'state': org_data['state'],
                    'zip_code': '12345',
                    'country': 'US'
                }
            )

            created_orgs.append((org_profile, location))
            status = 'Created' if created else 'Found existing'
            self.stdout.write(f'  {status} organization: {org_data["name"]}')

        return created_orgs

    def create_individual_providers(self):
        """Create 50 individual providers and associate with organizations."""
        
        provider_names = [
            ('Dr. Matthew', 'Johnson', 'PHYSICIAN', 'Internal Medicine'),
            ('Dr. Sarah', 'Williams', 'PHYSICIAN', 'Pediatrics'),
            ('Dr. Michael', 'Brown', 'PHYSICIAN', 'Cardiology'),
            ('Dr. Jennifer', 'Davis', 'PHYSICIAN', 'Dermatology'),
            ('Dr. David', 'Miller', 'PHYSICIAN', 'Orthopedics'),
            ('Dr. Lisa', 'Wilson', 'PHYSICIAN', 'Emergency Medicine'),
            ('Dr. Robert', 'Moore', 'PHYSICIAN', 'Surgery'),
            ('Dr. Ashley', 'Taylor', 'PHYSICIAN', 'Obstetrics'),
            ('Dr. Christopher', 'Anderson', 'PHYSICIAN', 'Neurology'),
            ('Dr. Amanda', 'Thomas', 'PHYSICIAN', 'Oncology'),
            ('Dr. James', 'Jackson', 'PHYSICIAN', 'Family Medicine'),
            ('Dr. Michelle', 'White', 'PHYSICIAN', 'Psychiatry'),
            ('Dr. Daniel', 'Harris', 'PHYSICIAN', 'Radiology'),
            ('Dr. Emily', 'Martin', 'PHYSICIAN', 'Endocrinology'),
            ('Dr. Andrew', 'Thompson', 'PHYSICIAN', 'Nephrology'),
            ('Dr. Jessica', 'Garcia', 'PHYSICIAN', 'Pulmonology'),
            ('Dr. Ryan', 'Martinez', 'PHYSICIAN', 'Gastroenterology'),
            ('Dr. Rachel', 'Robinson', 'PHYSICIAN', 'Rheumatology'),
            ('Dr. Kevin', 'Clark', 'PHYSICIAN', 'Urology'),
            ('Dr. Nicole', 'Rodriguez', 'PHYSICIAN', 'Anesthesiology'),
            ('Nurse', 'Patricia Lee', 'NURSE_PRACTITIONER', 'Critical Care'),
            ('Nurse', 'Mark Lewis', 'NURSE_PRACTITIONER', 'Emergency'),
            ('Nurse', 'Maria Walker', 'NURSE_PRACTITIONER', 'Pediatric'),
            ('Nurse', 'John Hall', 'NURSE_PRACTITIONER', 'Surgical'),
            ('Nurse', 'Linda Allen', 'NURSE_PRACTITIONER', 'Cardiac'),
            ('Dr. Steven', 'Young', 'PHYSICIAN', 'Ophthalmology'),
            ('Dr. Karen', 'Hernandez', 'PHYSICIAN', 'Otolaryngology'),
            ('Dr. Charles', 'King', 'PHYSICIAN', 'Plastic Surgery'),
            ('Dr. Nancy', 'Wright', 'PHYSICIAN', 'Pathology'),
            ('Dr. Paul', 'Lopez', 'PHYSICIAN', 'Sports Medicine'),
            ('Dr. Sharon', 'Hill', 'PHYSICIAN', 'Geriatrics'),
            ('Dr. Jason', 'Scott', 'PHYSICIAN', 'Infectious Disease'),
            ('Dr. Donna', 'Green', 'PHYSICIAN', 'Hematology'),
            ('Dr. Kenneth', 'Adams', 'PHYSICIAN', 'Allergy'),
            ('Dr. Carol', 'Baker', 'PHYSICIAN', 'Physical Medicine'),
            ('Nurse', 'Betty Gonzalez', 'NURSE_PRACTITIONER', 'Oncology'),
            ('Nurse', 'Edward Nelson', 'NURSE_PRACTITIONER', 'Mental Health'),
            ('Nurse', 'Dorothy Carter', 'NURSE_PRACTITIONER', 'Home Health'),
            ('Nurse', 'Ronald Mitchell', 'NURSE_PRACTITIONER', 'ICU'),
            ('Nurse', 'Helen Perez', 'NURSE_PRACTITIONER', 'Operating Room'),
            ('Dr. Gary', 'Roberts', 'PHYSICIAN', 'Vascular Surgery'),
            ('Dr. Ruth', 'Turner', 'PHYSICIAN', 'Nuclear Medicine'),
            ('Dr. Frank', 'Phillips', 'PHYSICIAN', 'Pain Management'),
            ('Dr. Laura', 'Campbell', 'PHYSICIAN', 'Occupational Medicine'),
            ('Dr. Jerry', 'Parker', 'PHYSICIAN', 'Sleep Medicine'),
            ('Nurse', 'Rose Evans', 'NURSE_PRACTITIONER', 'Dialysis'),
            ('Nurse', 'Wayne Edwards', 'NURSE_PRACTITIONER', 'Rehabilitation'),
            ('Nurse', 'Julia Collins', 'NURSE_PRACTITIONER', 'Wound Care'),
            ('Nurse', 'Arthur Stewart', 'NURSE_PRACTITIONER', 'Transplant'),
            ('Nurse', 'Gloria Sanchez', 'NURSE_PRACTITIONER', 'Labor & Delivery')
        ]

        # Get all organizations for random assignment
        organizations = list(OrganizationProfile.objects.all())
        
        created_providers = []
        
        for first_name, last_name, provider_type, specialty in provider_names:
            # Create provider user account
            first_clean = first_name.lower().replace('. ', '').replace('dr. ', '')
            last_clean = last_name.lower().replace(' ', '')
            email = f"{first_clean}.{last_clean}@healthcare.com"
            
            provider_user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'INDIVIDUAL_PROVIDER',
                }
            )
            
            if created:
                provider_user.set_password('testpass123')
                provider_user.save()

            # Create provider profile
            provider_profile, profile_created = IndividualProviderProfile.objects.get_or_create(
                user=provider_user,
                defaults={
                    'provider_type': provider_type,
                    'specialty': specialty,
                    'license_number': f"LIC{random.randint(100000, 999999)}",
                    'years_of_experience': random.randint(1, 30),
                    'bio': f"Experienced {specialty.lower()} specialist with a passion for patient care and medical excellence."
                }
            )

            # Associate with random organization (create separate location for provider)
            if organizations:
                org = random.choice(organizations)
                # Get organization's location details to create provider's location nearby
                org_location = org.locations.first()
                if org_location:
                    prov_location, prov_loc_created = ProviderLocation.objects.get_or_create(
                        individual_provider=provider_profile,
                        name=f"{first_name} {last_name} - {org.name}",
                        defaults={
                            'location_type': 'PRIVATE_PRACTICE',
                            'address': f"456 Medical Plaza (near {org_location.address})",
                            'city': org_location.city,
                            'state': org_location.state,
                            'zip_code': org_location.zip_code,
                            'country': org_location.country
                        }
                    )

            created_providers.append(provider_profile)
            status = 'Created' if created else 'Found existing'
            self.stdout.write(f'  {status} provider: {first_name} {last_name} ({specialty})')

        return created_providers

    def create_events(self):
        """Create 30 diverse events with proper associations."""
        
        # Get all categories and providers for event assignment
        categories = list(EventCategory.objects.all())
        providers = list(User.objects.filter(user_type__in=['INDIVIDUAL_PROVIDER', 'ORGANIZATION']))
        org_locations = list(ProviderLocation.objects.filter(organization__isnull=False))
        
        if not providers:
            self.stdout.write(self.style.WARNING('No providers found. Please create providers first.'))
            return

        event_templates = [
            {
                'title': 'Free Diabetes Screening Camp',
                'description': 'Comprehensive diabetes screening including blood sugar tests, HbA1c, and consultation with endocrinologists.',
                'category': 'Health Camps',
                'event_type': 'HEALTH_CAMP',
                'is_online': False,
                'requires_registration': True,
                'max_participants': 100
            },
            {
                'title': 'Heart Health Awareness Workshop',
                'description': 'Learn about cardiovascular health, risk factors, and prevention strategies from our cardiology experts.',
                'category': 'Workshops',
                'event_type': 'WORKSHOP',
                'is_online': False,
                'requires_registration': True,
                'max_participants': 50
            },
            {
                'title': 'Telemedicine Best Practices Webinar',
                'description': 'Online session covering the latest developments in telemedicine and digital health technologies.',
                'category': 'Webinars',
                'event_type': 'WEBINAR',
                'is_online': True,
                'online_platform': 'ZOOM',
                'requires_registration': True,
                'max_participants': 200
            },
            {
                'title': 'Mental Health Support Group Meeting',
                'description': 'Weekly support group for individuals dealing with anxiety and depression. Safe space for sharing and healing.',
                'category': 'Support Groups',
                'event_type': 'SUPPORT_GROUP',
                'is_online': False,
                'requires_registration': False
            },
            {
                'title': 'COVID-19 Vaccination Drive',
                'description': 'Community vaccination program offering COVID-19 vaccines and boosters. Walk-ins welcome.',
                'category': 'Vaccination Drives',
                'event_type': 'HEALTH_CAMP',
                'is_online': False,
                'requires_registration': False,
                'max_participants': 500
            },
            {
                'title': 'Cancer Prevention Seminar',
                'description': 'Educational seminar on cancer prevention, early detection methods, and lifestyle modifications.',
                'category': 'Seminars',
                'event_type': 'SEMINAR',
                'is_online': False,
                'requires_registration': True,
                'max_participants': 75
            },
            {
                'title': 'Free Pediatric Health Checkup',
                'description': 'Comprehensive health checkups for children ages 1-12. Includes growth assessment and immunization review.',
                'category': 'Free Consultations',
                'event_type': 'CONSULTATION',
                'is_online': False,
                'requires_registration': True,
                'max_participants': 60
            },
            {
                'title': 'Women\'s Health Screening Event',
                'description': 'Comprehensive screening including mammography, pap smear, and bone density testing.',
                'category': 'Health Screenings',
                'event_type': 'SCREENING',
                'is_online': False,
                'requires_registration': True,
                'max_participants': 80
            },
            {
                'title': 'Nutrition and Wellness Workshop',
                'description': 'Interactive workshop on healthy eating habits, meal planning, and sustainable lifestyle changes.',
                'category': 'Workshops',
                'event_type': 'WORKSHOP',
                'is_online': True,
                'online_platform': 'GOOGLE_MEET',
                'requires_registration': True,
                'max_participants': 40
            },
            {
                'title': 'Senior Health and Wellness Fair',
                'description': 'Health fair specifically designed for seniors, featuring health screenings and wellness resources.',
                'category': 'Health Camps',
                'event_type': 'HEALTH_CAMP',
                'is_online': False,
                'requires_registration': False,
                'max_participants': 150
            }
        ]

        # Generate 30 events by repeating and modifying templates
        created_events = []
        
        for i in range(30):
            template = event_templates[i % len(event_templates)]
            
            # Create unique variations
            event_number = i + 1
            title_suffix = f" #{event_number}" if i >= len(event_templates) else ""
            
            # Random date between today and 3 months from now
            start_date = date.today() + timedelta(days=random.randint(1, 90))
            
            # Random time during business hours (8 AM to 6 PM)
            start_time = time(
                hour=random.randint(8, 17),
                minute=random.choice([0, 15, 30, 45])
            )
            
            # End time 1-3 hours after start
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = start_datetime + timedelta(hours=random.randint(1, 3))
            end_time = end_datetime.time()
            
            # Get category
            category = None
            if template['category'] and categories:
                category = next((c for c in categories if c.name == template['category']), None)
            
            # Select random provider
            provider = random.choice(providers)
            
            # Determine location
            location = None
            online_platform = None
            online_link = None
            
            if template['is_online']:
                online_platform = template.get('online_platform', 'ZOOM')
                online_link = f"https://{online_platform.lower()}.com/j/{random.randint(1000000, 9999999)}"
            else:
                if org_locations:
                    location = random.choice(org_locations)
            
            # Create event
            event = Event.objects.create(
                created_by=provider,
                title=template['title'] + title_suffix,
                description=template['description'],
                category=category,
                event_type=template['event_type'],
                location=location,
                is_online=template['is_online'],
                online_platform=online_platform,
                online_link=online_link,
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                requires_registration=template['requires_registration'],
                max_participants=template.get('max_participants'),
                registration_deadline=timezone.now() + timedelta(days=random.randint(1, 30)) if template['requires_registration'] else None,
                registration_fee=Decimal(random.choice([0, 10, 25, 50])) if template['requires_registration'] else Decimal('0.00'),
                is_published=True,
                is_featured=random.choice([True, False])
            )
            
            created_events.append(event)
            venue_info = "Online" if event.is_online else (location.name if location else "TBD")
            self.stdout.write(f'  Created event: {event.title} ({venue_info})')

        return created_events