from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
from email.utils import formataddr

def  send_styled_email(subject, context, recipient_list, template):
    # Render HTML content from template
    html_content = render_to_string(f"emails/{template}", context)

    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)

    from_email = formataddr(("UrbanMD Health Network", settings.DEFAULT_FROM_EMAIL))

    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()


def send_welcome_email(name, email):
    # Send welcome email to new user
    welcome_subject = 'Welcome to UrbanMD Health Network - Early Access Confirmed!'
    context = {
        'name': name.split()[0] if name else 'Valued User',
        'portal_url': settings.PORTAL_URL,
    }

    send_styled_email(
        subject=welcome_subject,
        context=context,
        recipient_list=[email],
        template='campaign_email.html'
    )

def send_contact_admin_notification(first_name, last_name, email, phone, subject, message):
    """Send notification email to admin about new contact form submission"""
    admin_subject = f'UrbanMD Contact Form: {subject}'

    context = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'subject': subject,
        'message': message,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
    }

    send_styled_email(
        subject=admin_subject,
        context=context,
        recipient_list=["livewell@urbanmdtv.com"],
        template='contact_admin_notification.html'
    )

def send_contact_user_confirmation(first_name, email, subject, message):
    """Send confirmation email to user who submitted the contact form"""
    confirmation_subject = 'Thank you for contacting UrbanMD Health Network'

    # Create a preview of the message (first 100 characters)
    message_preview = message[:100] if len(message) > 100 else None

    context = {
        'first_name': first_name,
        'subject': subject,
        'message_preview': message_preview,
        'portal_url': settings.PORTAL_URL,
    }

    send_styled_email(
        subject=confirmation_subject,
        context=context,
        recipient_list=[email],
        template='contact_user_confirmation.html'
    )


def send_promotional_email_fn(subject, context, recipient_list):
    """Send promotional email to a list of recipients"""
    # Render HTML content from template
    html_content = render_to_string("emails/promotional_email.html", context)

    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)

    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()