from django.db import models


class Subscription(models.Model):
    """Doctor's platform subscription."""

    doctor = models.OneToOneField(
        'accounts.IndividualProviderProfile',
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    PLAN_CHOICES = [
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('ENTERPRISE', 'Enterprise'),
    ]

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='BASIC')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAST_DUE', 'Past Due'),
        ('CANCELLED', 'Cancelled'),
        ('TRIAL', 'Trial'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')

    start_date = models.DateField()
    next_billing_date = models.DateField()

    payment_method = models.CharField(max_length=50, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.plan} Plan"


class Payment(models.Model):
    """Record of payments made by doctors to the platform."""

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    transaction_id = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=50)

    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscription.doctor.user.full_name} - ${self.amount} ({self.payment_date.strftime('%Y-%m-%d')})"