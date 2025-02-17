from django.contrib.auth.models import User
from django.core.mail import send_mail

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Event

@receiver(m2m_changed, sender=Event.rsvps.through)
def send_rsvp_confirmation(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            user = model.objects.get(pk=user_id)
            subject = f"RSVP Confirmation for {instance.name}"
            message = f"Hello {user.username},\n\nYou have successfully RSVP'd for {instance.name} on {instance.date} at {instance.time}.\n\nSee you there!"
            user_email = user.email

            send_mail(
                subject,
                message,
                'habib6bd@gmail.com',
                [user_email],
                fail_silently=False,
            )
