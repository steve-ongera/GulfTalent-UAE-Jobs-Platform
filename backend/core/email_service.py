from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def _send(subject, to_email, template, context):
    context.update({'site_name': settings.SITE_NAME, 'site_url': settings.SITE_URL})
    html = render_to_string(template, context)
    msg = EmailMultiAlternatives(subject, subject, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html, 'text/html')
    msg.send()


def send_application_received(application):
    _send(
        subject=f'Application Received — {application.job.title} | GulfTalent',
        to_email=application.email,
        template='application_received.html',
        context={
            'applicant_name': application.full_name,
            'job_title': application.job.title,
            'job_emirate': application.job.get_emirate_display(),
            'category': application.job.category.name,
            'application_id': application.id,
            'applied_at': application.applied_at,
        }
    )
    _send(
        subject=f'New Application: {application.full_name} → {application.job.title}',
        to_email=settings.ADMIN_NOTIFICATION_EMAIL,
        template='application_admin_notify.html',
        context={
            'applicant_name': application.full_name,
            'applicant_email': application.email,
            'applicant_phone': application.phone,
            'job_title': application.job.title,
            'job_emirate': application.job.get_emirate_display(),
            'category': application.job.category.name,
            'cover_letter': application.cover_letter,
            'admin_url': f"{settings.SITE_URL}/admin/applications/{application.id}",
            'application_id': application.id,
        }
    )


def send_status_update(application):
    messages = {
        'reviewed': 'Your application is currently being reviewed by our team.',
        'shortlisted': 'Great news! You have been shortlisted for this position.',
        'rejected': 'Thank you for your interest. After careful review, we will not be moving forward at this time.',
        'hired': 'Congratulations! You have been selected for this position.',
    }
    _send(
        subject=f'Application Update — {application.job.title} | GulfTalent',
        to_email=application.email,
        template='status_update.html',
        context={
            'applicant_name': application.full_name,
            'job_title': application.job.title,
            'status': application.get_status_display(),
            'status_message': messages.get(application.status, ''),
            'admin_notes': application.admin_notes,
            'application_id': application.id,
        }
    )