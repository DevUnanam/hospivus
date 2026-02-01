import os
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class MedicalCondition(models.Model):
    """
    Model representing a medical condition or disease.
    Provides an A-Z index of medical conditions similar to Mayo Clinic.
    """
    DEPARTMENTS = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'), 
        ('orthopedics', 'Orthopedics'),
        ('dermatology', 'Dermatology'),
        ('gastroenterology', 'Gastroenterology'),
        ('pulmonology', 'Pulmonology'),
        ('endocrinology', 'Endocrinology'),
        ('oncology', 'Oncology'),
        ('psychiatry', 'Psychiatry'),
        ('pediatrics', 'Pediatrics'),
        ('obstetrics_gynecology', 'Obstetrics & Gynecology'),
        ('internal_medicine', 'Internal Medicine'),
        ('emergency_medicine', 'Emergency Medicine'),
        ('radiology', 'Radiology'),
        ('anesthesiology', 'Anesthesiology'),
        ('pathology', 'Pathology'),
        ('urology', 'Urology'),
        ('ophthalmology', 'Ophthalmology'),
        ('otolaryngology', 'Otolaryngology (ENT)'),
        ('rheumatology', 'Rheumatology'),
        ('infectious_disease', 'Infectious Disease'),
        ('nephrology', 'Nephrology'),
        ('hematology', 'Hematology'),
        ('general_surgery', 'General Surgery'),
    ]

    name = models.CharField(
        max_length=200, 
        unique=True,
        help_text="Name of the medical condition"
    )
    slug = models.SlugField(
        max_length=220, 
        unique=True, 
        blank=True,
        help_text="URL-friendly version of the name (auto-generated)"
    )
    overview = models.TextField(
        help_text="Brief overview or description of the condition"
    )
    symptoms = models.TextField(
        help_text="Signs and symptoms of the condition"
    )
    causes = models.TextField(
        help_text="Causes and risk factors"
    )
    treatments = models.TextField(
        help_text="Treatment options and management strategies"
    )
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENTS,
        help_text="Medical department/specialty that typically handles this condition"
    )
    image = models.ImageField(
        upload_to='conditions/',
        null=True,
        blank=True,
        help_text="Representative image for this condition"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Medical Condition"
        verbose_name_plural = "Medical Conditions"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['department']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while MedicalCondition.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def first_letter(self):
        """Returns the first letter of the condition name in uppercase"""
        return self.name[0].upper() if self.name else ''
    
    @property
    def department_display(self):
        """Returns the human-readable department name"""
        return dict(self.DEPARTMENTS).get(self.department, self.department)

    def get_absolute_url(self):
        """Returns the canonical URL for this condition"""
        return reverse('health_tech:condition_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def get_related_conditions(self, limit=5):
        """Get related conditions from the same department"""
        return MedicalCondition.objects.filter(
            department=self.department
        ).exclude(
            id=self.id
        ).order_by('name')[:limit]