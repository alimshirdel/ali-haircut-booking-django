from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation
from .tasks import schedule_sms_reminder
from datetime import datetime


@receiver(post_save, sender=Reservation)
def setup_sms_reminder(sender, instance, created, **kwargs):
    if created:
        reservation_datetime = datetime.combine(
            instance.schedule.date, instance.time_slot
        )
        reservation_str = reservation_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # تبدیل به string
        schedule_sms_reminder.send(
            instance.user.get_full_name(),  # نام کاربر
            instance.user.phone_number,  # شماره تلفن
            reservation_str,  # رشته قابل JSON
        )
