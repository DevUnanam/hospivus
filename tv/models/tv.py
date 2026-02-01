from django.db import models
from django.utils.text import slugify


class VideoCategory(models.Model):
    """Category for organizing videos"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    icon = models.CharField(max_length=50, help_text="Icon class name")
    color = models.CharField(max_length=20, default="blue", help_text="Color theme for category")
    description = models.TextField(blank=True)
    count = models.PositiveIntegerField(default=0, help_text="Number of videos in this category")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Video Categories"


class VideoSource(models.Model):
    """Source of health videos"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    is_partner = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Video(models.Model):
    """Video model for health-related content"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, related_name='videos')
    thumbnail = models.ImageField(upload_to='video_thumbnails/')
    video_url = models.URLField(help_text="YouTube URL or other video embed URL")
    duration = models.DurationField(help_text="Duration of the video")
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    source = models.ForeignKey(VideoSource, on_delete=models.SET_NULL, null=True, related_name='videos')
    presenter = models.CharField(max_length=100, help_text="Name of doctor or presenter")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserVideoInteraction(models.Model):
    """Track user interactions with videos"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    watch_progress = models.PositiveIntegerField(default=0, help_text="Progress in seconds")
    watched_at = models.DateTimeField(auto_now=True)
    is_saved = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="User rating 1-5")

    class Meta:
        unique_together = ('user', 'video')