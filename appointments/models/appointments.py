from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError


# class OfficeHours(models.Model):
#     """Doctor's office hours schedule."""

#     doctor = models.ForeignKey(
#         'accounts.IndividualProviderProfile',
#         on_delete=models.CASCADE,
#         related_name='office_hours'
#     )
#     location = models.ForeignKey(
#         'accounts.ProviderLocation',
#         on_delete=models.CASCADE,
#         related_name='hours'
#     )

#     DAY_CHOICES = [
#         (0, 'Monday'),
#         (1, 'Tuesday'),
#         (2, 'Wednesday'),
#         (3, 'Thursday'),
#         (4, 'Friday'),
#         (5, 'Saturday'),
#         (6, 'Sunday'),
#     ]

#     day_of_week = models.IntegerField(choices=DAY_CHOICES)
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     is_available = models.BooleanField(default=True)

#     class Meta:
#         ordering = ['day_of_week', 'start_time']

#     def __str__(self):
#         return f"{self.get_day_of_week_display()}: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class Appointment(models.Model):
    """Appointment between patient and doctor."""

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    APPOINTMENT_TYPE_CHOICES = [
        ('IN_PERSON', 'In-Person'),
        ('VIDEO', 'Video Consultation'),
        ('PHONE', 'Phone Consultation'),
    ]

    patient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'user_type': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    location = models.ForeignKey(
        'accounts.ProviderLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )

    # Appointment details
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES,
        default='IN_PERSON'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )

    # Medical information
    reason_for_visit = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)

    # Video consultation details (if applicable)
    video_link = models.URLField(blank=True, null=True)
    video_room_id = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = [['doctor', 'date', 'start_time']]

    def __str__(self):
        return f"{self.patient.full_name} - Dr. {self.doctor.user.full_name} on {self.date} at {self.start_time}"

    def clean(self):
        """Validate appointment data."""
        if self.date < timezone.now().date():
            raise ValidationError("Cannot schedule appointments in the past.")

        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        # Check if doctor is available at this time
        if self.doctor and self.date and self.start_time and self.end_time:
            conflicting_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                status__in=['SCHEDULED', 'CONFIRMED', 'IN_PROGRESS']
            ).exclude(pk=self.pk)

            for appointment in conflicting_appointments:
                if (self.start_time < appointment.end_time and
                    self.end_time > appointment.start_time):
                    raise ValidationError(
                        "Doctor already has an appointment at this time."
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate appointment duration in minutes."""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)
        return int((end_datetime - start_datetime).total_seconds() / 60)

    @property
    def is_upcoming(self):
        """Check if appointment is in the future."""
        appointment_datetime = datetime.combine(self.date, self.start_time)
        return appointment_datetime > datetime.now() and self.status in ['SCHEDULED', 'CONFIRMED']

    @property
    def is_today(self):
        """Check if appointment is today."""
        return self.date == timezone.now().date()

    def confirm(self):
        """Confirm the appointment."""
        self.status = 'CONFIRMED'
        self.confirmed_at = timezone.now()
        self.save()

    def cancel(self, reason=''):
        """Cancel the appointment."""
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()

    def mark_completed(self):
        """Mark appointment as completed."""
        self.status = 'COMPLETED'
        self.save()

    def mark_no_show(self):
        """Mark appointment as no-show."""
        self.status = 'NO_SHOW'
        self.save()

    def start_appointment(self):
        """Start the appointment (mark as in progress)."""
        self.status = 'IN_PROGRESS'
        self.save()


class OfficeHours(models.Model):
    """Doctor's office hours/availability."""

    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='office_hours'
    )
    location = models.ForeignKey(
        'accounts.ProviderLocation',
        on_delete=models.CASCADE,
        related_name='office_hours',
        null=True,
        blank=True
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Appointment settings
    slot_duration = models.IntegerField(
        default=30,
        help_text="Duration of each appointment slot in minutes"
    )
    buffer_time = models.IntegerField(
        default=0,
        help_text="Buffer time between appointments in minutes"
    )

    # Break time (optional)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = [['doctor', 'location', 'day_of_week', 'start_time']]

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"

    def clean(self):
        """Validate office hours."""
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        if self.break_start and self.break_end:
            if self.break_start >= self.break_end:
                raise ValidationError("Break end time must be after break start time.")

            if self.break_start < self.start_time or self.break_end > self.end_time:
                raise ValidationError("Break time must be within office hours.")

    def get_available_slots(self, date):
        """Get available appointment slots for a specific date."""
        # Check if the date matches this office hour's day of week
        if date.weekday() != self.day_of_week:
            return []

        # Get all appointments for this doctor on this date
        existing_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            date=date,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).values_list('start_time', 'end_time')

        # Generate all possible slots
        slots = []
        current_time = datetime.combine(date, self.start_time)
        end_time = datetime.combine(date, self.end_time)
        slot_duration = timedelta(minutes=self.slot_duration)
        buffer_duration = timedelta(minutes=self.buffer_time)

        while current_time + slot_duration <= end_time:
            slot_start = current_time.time()
            slot_end = (current_time + slot_duration).time()

            # Check if slot is during break time
            if self.break_start and self.break_end:
                if not (slot_end <= self.break_start or slot_start >= self.break_end):
                    current_time += slot_duration + buffer_duration
                    continue

            # Check if slot conflicts with existing appointments
            is_available = True
            for apt_start, apt_end in existing_appointments:
                if not (slot_end <= apt_start or slot_start >= apt_end):
                    is_available = False
                    break

            if is_available:
                # Check if slot is in the past for today
                if date == timezone.now().date() and slot_start <= timezone.now().time():
                    is_available = False

                slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end,
                    'is_available': is_available
                })

            current_time += slot_duration + buffer_duration

        return slots


class AppointmentReminder(models.Model):
    """Reminders for appointments."""

    REMINDER_TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(
        max_length=10,
        choices=REMINDER_TYPE_CHOICES
    )
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return f"{self.reminder_type} reminder for {self.appointment}"

    def send(self):
        """Send the reminder (placeholder for actual implementation)."""
        # TODO: Implement actual sending logic based on reminder_type
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()


class WaitList(models.Model):
    """Waitlist for appointments."""

    patient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='waitlist_entries',
        limit_choices_to={'user_type': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='waitlist_entries'
    )
    preferred_dates = models.JSONField(
        default=list,
        help_text="List of preferred dates for appointment"
    )
    preferred_times = models.JSONField(
        default=dict,
        help_text="Preferred time ranges (morning, afternoon, evening)"
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=Appointment.APPOINTMENT_TYPE_CHOICES,
        default='IN_PERSON'
    )
    reason_for_visit = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        unique_together = [['patient', 'doctor', 'is_active']]

    def __str__(self):
        return f"Waitlist: {self.patient.full_name} waiting for Dr. {self.doctor.user.full_name}"

    def notify_availability(self, available_slot):
        """Notify patient about available slot."""
        # TODO: Implement notification logic
        self.notified_at = timezone.now()
        self.save()

    def deactivate(self):
        """Deactivate waitlist entry."""
        self.is_active = False
        self.save()