from django.db import models


class Service(models.Model):
    """Services offered by doctors nationwide."""

    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='services'
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)

    is_virtual = models.BooleanField(default=False)
    is_home_visit = models.BooleanField(default=False)

    SERVICE_TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('TREATMENT', 'Treatment'),
        ('PROCEDURE', 'Procedure'),
        ('THERAPY', 'Therapy'),
        ('TEST', 'Diagnostic Test'),
        ('OTHER', 'Other'),
    ]

    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceArea(models.Model):
    """Geographic areas where doctors offer their services."""

    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='service_areas'
    )

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    radius_miles = models.PositiveIntegerField(default=25, help_text="Service radius in miles")

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city}, {self.state} {self.zip_code} ({self.radius_miles} miles)"