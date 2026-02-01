from django import forms
from .models import Campaign_Email
from django.core.validators import MinLengthValidator

class CampaignEmailForm(forms.ModelForm):
    """Form for collecting email for the campaign"""
    name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Your Name (Optional)'
        })
    )
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Your Email Address'
        })
    )

    class Meta:
        model = Campaign_Email
        fields = ['name', 'email']


# Contact Form
class ContactForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]',
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]',
            'placeholder': 'Doe'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]',
            'placeholder': 'john.doe@example.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]',
            'placeholder': '+1 (312) 555-1234'
        })
    )
    subject = forms.ChoiceField(
        choices=[
            ('', 'Select a subject'),
            ('general', 'General Inquiry'),
            ('partnership', 'Partnership Opportunities'),
            ('provider', 'Healthcare Provider Registration'),
            ('technical', 'Technical Support'),
            ('media', 'Media Inquiry'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#00b6d8]',
            'rows': 5,
            'placeholder': 'Tell us how we can help you...'
        })
    )


class PromotionalEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter email subject...'
        }),
        validators=[MinLengthValidator(5, 'Subject must be at least 5 characters long')]
    )

    preview_text = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Email preview text (optional)...'
        }),
        help_text='This text appears in email inbox preview'
    )

    headline = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Main headline for the email...'
        })
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 8,
            'placeholder': 'Enter your promotional message here...'
        }),
        validators=[MinLengthValidator(20, 'Content must be at least 20 characters long')]
    )

    cta_text = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Call to action button text (e.g., Learn More)'
        })
    )

    cta_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'https://example.com'
        })
    )

    send_test = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label='Send test email to admin first'
    )

    test_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'admin@example.com'
        }),
        help_text='Email address for test send'
    )

    def clean(self):
        cleaned_data = super().clean()
        cta_text = cleaned_data.get('cta_text')
        cta_url = cleaned_data.get('cta_url')
        send_test = cleaned_data.get('send_test')
        test_email = cleaned_data.get('test_email')

        # If CTA text is provided, URL must also be provided
        if cta_text and not cta_url:
            raise forms.ValidationError('Call to action URL is required when button text is provided')

        # If sending test, test email must be provided
        if send_test and not test_email:
            raise forms.ValidationError('Test email address is required when sending test email')

        return cleaned_data