from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class EventCategory(models.Model):
    """Event categories."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # CSS class or emoji
    color = models.CharField(max_length=20, blank=True, null=True)  # CSS color class

    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    """Events posted by healthcare providers on the bulletin board."""

    # Creator (only non-patients can create events)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events',
        limit_choices_to=~models.Q(user_type='PATIENT')
    )

    # Event details
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    # Location details
    location = models.ForeignKey(
        'accounts.ProviderLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    # For online events
    is_online = models.BooleanField(default=False)
    online_platform = models.CharField(
        max_length=50,
        choices=[
            ('ZOOM', 'Zoom'),
            ('GOOGLE_MEET', 'Google Meet'),
            ('TEAMS', 'Microsoft Teams'),
            ('WEBEX', 'Cisco Webex'),
            ('OTHER', 'Other')
        ],
        blank=True,
        null=True
    )
    online_link = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    meeting_password = models.CharField(max_length=50, blank=True, null=True)

    # Date and time
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Registration details
    requires_registration = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Media
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    # Status
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Legacy field for backward compatibility
    EVENT_TYPE_CHOICES = [
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('WEBINAR', 'Webinar'),
        ('CONSULTATION', 'Free Consultation'),
        ('HEALTH_CAMP', 'Health Camp'),
        ('SCREENING', 'Health Screening'),
        ('SUPPORT_GROUP', 'Support Group'),
        ('OTHER', 'Other'),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='OTHER')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        return self.start_date >= timezone.now().date()

    @property
    def is_past(self):
        """Check if event is past"""
        return self.start_date < timezone.now().date()

    @property
    def venue_display(self):
        """Get formatted venue display"""
        if self.is_online:
            return f"Online via {self.get_online_platform_display() if self.online_platform else 'Virtual Event'}"
        elif self.location:
            return str(self.location)
        else:
            return "Venue TBD"

    @property
    def registration_open(self):
        """Check if registration is still open"""
        if not self.requires_registration:
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        if self.max_participants:
            return self.registrations.count() < self.max_participants
        return True

    def save(self, *args, **kwargs):
        # Auto-set end_date if not provided
        if not self.end_date:
            self.end_date = self.start_date
        super().save(*args, **kwargs)


class EventRegistration(models.Model):
    """Event registrations by users."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.full_name} - {self.event.title}"


class SavedEvent(models.Model):
    """Events saved by users for later reference."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_events'
    )
    saved_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-saved_date']

    def __str__(self):
        return f"{self.user.full_name} saved {self.event.title}"