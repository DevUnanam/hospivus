import threading
from django.http import JsonResponse
from django.views.generic import FormView

from email_campaign.functions import send_contact_admin_notification, send_contact_user_confirmation, send_promotional_email_fn, send_styled_email, send_welcome_email
from email_campaign.models.campaign import EmailLog
from .forms import CampaignEmailForm, ContactForm, PromotionalEmailForm
from .models import Campaign_Email

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)

def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_or_admin, login_url='email_campaign:email_campaign') # Change login url later
def send_promotional_email(request):
    if request.method == 'POST':
        form = PromotionalEmailForm(request.POST)
        if form.is_valid():
            # Get form data
            subject = form.cleaned_data['subject']
            preview_text = form.cleaned_data.get('preview_text', '')
            headline = form.cleaned_data['headline']
            content = form.cleaned_data['content']
            cta_text = form.cleaned_data.get('cta_text', '')
            cta_url = form.cleaned_data.get('cta_url', '')
            send_test = form.cleaned_data['send_test']
            test_email = form.cleaned_data.get('test_email', '')

            # Prepare email context
            email_context = {
                'subject': subject,
                'preview_text': preview_text,
                'headline': headline,
                'content': content,
                'cta_text': cta_text,
                'cta_url': cta_url,
                'current_year': timezone.now().year,
            }

            try:
                if send_test and test_email:
                    # Send test email
                    send_promotional_email_fn(subject, email_context, [test_email])

                    messages.success(request, f'Test email sent successfully to {test_email}!')
                    return render(request, 'send_promotional.html', {
                        'form': form,
                        'preview_context': email_context,
                        'show_preview': True
                    })
                else:
                    # Send to all active subscribers
                    subscribers = Campaign_Email.objects.filter(is_active=True)
                    total_sent = 0
                    failed = 0

                    for subscriber in subscribers:
                        try:
                            # Add personalization
                            personalized_context = email_context.copy()
                            personalized_context['name'] = subscriber.name.split()[0] if subscriber.name else 'Valued Member'
                            personalized_context['email'] = subscriber.email

                            # Send email
                            send_promotional_email_fn(subject, personalized_context, [subscriber.email])

                            total_sent += 1

                            # Log the email send
                            EmailLog.objects.create(
                                subscriber=subscriber,
                                subject=subject,
                                sent_at=timezone.now(),
                                status='sent'
                            )

                        except Exception as e:
                            failed += 1
                            logger.error(f"Failed to send email to {subscriber.email}: {str(e)}")

                            # Log the failure
                            EmailLog.objects.create(
                                subscriber=subscriber,
                                subject=subject,
                                sent_at=timezone.now(),
                                status='failed',
                                error_message=str(e)
                            )

                    # Show results
                    if total_sent > 0:
                        messages.success(request, f'Promotional email sent successfully to {total_sent} subscribers!')
                    if failed > 0:
                        messages.warning(request, f'{failed} emails failed to send. Check logs for details.')

                    return redirect('email_campaign:send_promotional_email')

            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                logger.error(f"Email send error: {str(e)}")
    else:
        form = PromotionalEmailForm()

    # Get statistics for display
    total_subscribers = Campaign_Email.objects.filter(is_active=True).count()
    recent_emails = EmailLog.objects.select_related('subscriber').order_by('-sent_at')[:10]

    return render(request, 'send_promotional.html', {
        'form': form,
        'total_subscribers': total_subscribers,
        'recent_emails': recent_emails,
    })


class EmailCampaignView(FormView):
    """View for email campaign landing page and form submission"""
    template_name = 'email_campaign.html'
    form_class = CampaignEmailForm
    success_url = '#'

    def form_valid(self, form):
        """Handle form submission"""
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']

        # Check if email already exists
        try:
            existing_email = Campaign_Email.objects.get(email=email)
            # Increment counter if email exists
            existing_email.seen_counter += 1
            if name and not existing_email.name:
                existing_email.name = name
            existing_email.save()
            is_new = False
        except Campaign_Email.DoesNotExist:
            # Create new record if email doesn't exist
            form.save()
            is_new = True

            t = threading.Thread(target=send_welcome_email, args=(name, email))
            t.daemon = True
            t.start()

        # Return JSON response for AJAX
        return JsonResponse({
            'success': True,
            'is_new': is_new,
            'message': 'Thank you for joining our waiting list!' if is_new else 'Great to see you again! We\'ve updated your information.'
        })

    def form_invalid(self, form):
        """Handle invalid form submission"""
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


@csrf_protect
def contact_view(request):
    if request.method == 'POST':
        # Handle AJAX form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = ContactForm(request.POST)

            if form.is_valid():
                # Extract form data
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                subject_key = form.cleaned_data['subject']
                message = form.cleaned_data['message']

                # Get the subject display name
                subject_dict = dict(form.fields['subject'].choices)
                subject = subject_dict.get(subject_key, 'General Inquiry')

                try:
                    # Send emails in background threads
                    # Admin notification
                    admin_thread = threading.Thread(
                        target=send_contact_admin_notification,
                        args=(first_name, last_name, email, phone, subject, message)
                    )
                    admin_thread.daemon = True
                    admin_thread.start()

                    # User confirmation
                    user_thread = threading.Thread(
                        target=send_contact_user_confirmation,
                        args=(first_name, email, subject, message)
                    )
                    user_thread.daemon = True
                    user_thread.start()

                    return JsonResponse({
                        'success': True,
                        'message': 'Your message has been sent successfully!'
                    })

                except Exception as e:
                    # Log the error
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error sending contact form emails: {str(e)}")

                    return JsonResponse({
                        'success': False,
                        'message': 'An error occurred while sending your message. Please try again later.'
                    })

            else:
                # Return form errors
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list

                return JsonResponse({
                    'success': False,
                    'errors': errors
                })

        # Handle regular form submission (non-AJAX)
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            subject_key = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Get the subject display name
            subject_dict = dict(form.fields['subject'].choices)
            subject = subject_dict.get(subject_key, 'General Inquiry')

            try:
                # Send emails in background threads
                admin_thread = threading.Thread(
                    target=send_contact_admin_notification,
                    args=(first_name, last_name, email, phone, subject, message)
                )
                admin_thread.daemon = True
                admin_thread.start()

                user_thread = threading.Thread(
                    target=send_contact_user_confirmation,
                    args=(first_name, email, subject, message)
                )
                user_thread.daemon = True
                user_thread.start()

                # Add success message to context
                return render(request, 'contact.html', {
                    'form': ContactForm(),  # Reset form
                    'success': True
                })

            except Exception as e:
                # Log the error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error sending contact form emails: {str(e)}")

                # Show form with error
                form.add_error(None, 'An error occurred while sending your message. Please try again later.')

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def unsubscribe_view(request):
    email = request.GET.get('email')
    if email:
        try:
            subscriber = Campaign_Email.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()

            messages.success(request, 'You have been successfully unsubscribed from our mailing list.')
        except Campaign_Email.DoesNotExist:
            messages.warning(request, 'Email address not found in our records.')
    else:
        messages.warning(request, 'No email address provided for unsubscription.')
    return render(request, 'unsubscribe.html', {
        'email': email,
    })
