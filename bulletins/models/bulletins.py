from django.db import models


class Event(models.Model):
    """Events posted by doctors on the bulletin board."""

    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='events'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.ForeignKey(
        'accounts.ProviderLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    location_details = models.CharField(max_length=255, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    is_published = models.BooleanField(default=True)

    EVENT_TYPE_CHOICES = [
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('WEBINAR', 'Webinar'),
        ('CONSULTATION', 'Free Consultation'),
        ('HEALTH_CAMP', 'Health Camp'),
        ('OTHER', 'Other'),
    ]

    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='OTHER')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return self.title