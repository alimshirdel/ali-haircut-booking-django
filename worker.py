import django
django.setup()  # فقط اینجا setup کنیم

from shops.tasks import schedule_sms_reminder, delete_expired_schedule

# اجرای dramatiq worker
# dramatiq مربوط به tasks.py اینجا اجرا میشه
