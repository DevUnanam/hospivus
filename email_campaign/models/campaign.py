from django.db import models


class Campaign_Email(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255)
    seen_counter = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailLog(models.Model):
    subscriber = models.ForeignKey(Campaign_Email, on_delete=models.CASCADE, related_name='email_logs')
    subject = models.CharField(max_length=200)
    sent_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ])
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} - {self.subscriber.email} ({self.status})"