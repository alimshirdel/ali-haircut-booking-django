from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation, Schedule
from .tasks import schedule_sms_reminder, delete_expired_schedule
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
            instance.id,
        )


@receiver(post_save, sender=Schedule)
def schedule_auto_delete(sender, instance, created, **kwargs):
    if created:
        schedule_datetime = datetime.combine(instance.date, instance.end_time)
        delay_seconds = (schedule_datetime - datetime.now()).total_seconds()

        if delay_seconds > 0:
            delete_expired_schedule.send_with_options(
                args=(instance.id,), delay=int(delay_seconds * 1000)
            )
            print(
                f"⏰ Schedule {instance.id} will be auto-deleted in {delay_seconds/60:.1f} minutes."
            )
        else:
            # اگه از قبل گذشته، همین الان حذفش کن
            instance.delete()
