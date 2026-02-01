from django.db import models
from django.utils import timezone


class Task(models.Model):
    """User health tasks with timing functionality."""

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Task timing
    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Recurrence
    RECURRENCE_CHOICES = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='NONE')

    # Priority
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    # Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SKIPPED', 'Skipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Task type for categorization
    TYPE_CHOICES = [
        ('MEDICATION', 'Medication'),
        ('EXERCISE', 'Exercise'),
        ('DIET', 'Diet'),
        ('MEASUREMENT', 'Health Measurement'),
        ('APPOINTMENT', 'Appointment Preparation'),
        ('OTHER', 'Other'),
    ]
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='OTHER')

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Reminders
    reminder_enabled = models.BooleanField(default=False)
    reminder_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', 'priority', 'start_time']

    def __str__(self):
        return self.title

    def complete(self):
        """Mark task as completed."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date:
            return False
        return self.due_date < timezone.now().date() and self.status != 'COMPLETED'