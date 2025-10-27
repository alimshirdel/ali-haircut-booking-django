from dramatiq import actor
from django.utils import timezone
from jalali_date import datetime2jalali
from datetime import datetime, timedelta
from .models import Schedule, Reservation
import requests, time, dramatiq, random
from django.conf import settings


@dramatiq.actor
def send_sms_reminder(phone_number, message, instance_id):
    try:
        reservation = Reservation.objects.get(id=instance_id)
    except reservation.DoesNotExist:
        print(f"⚠️ رزرو {instance_id} پیدا نشد، پیامک ارسال نشد.")
        return
    time.sleep(random.randint(3, 5))
    try:
        url = settings.MELIPAYAMAK_URL_SIMPLE
        payload = {"to": str(phone_number), "text": message}
        response = requests.post(url, json=payload, timeout=10)
        data = response.json() if response.content else {}

        if response.ok:
            print(f"✅ پیامک با موفقیت برای {phone_number} ارسال شد.")
            print("📨 پاسخ ملی پیامک:", data)
        else:
            print(f"❌ خطا در ارسال پیامک به {phone_number}:")
            print("🔹 وضعیت:", response.status_code)
            print("🔹 پاسخ:", data)

    except requests.Timeout:
        print(f"⏳ خطای Timeout در ارسال پیامک به {phone_number}")
    except Exception as e:
        print(f"⚠️ خطای کلی در ارسال پیامک به {phone_number}: {e}")


@dramatiq.actor
def schedule_sms_reminder(user_name, phone_number, reservation_str, instance_id):
    try:
        # تبدیل رشته به datetime
        print(reservation_str)
        reservation_datetime = datetime.strptime(reservation_str, "%Y-%m-%d %H:%M:%S")
        reservation_datetime = timezone.make_aware(reservation_datetime)
        # محاسبه زمان یادآوری (یک روز قبل)
        reminder_time = reservation_datetime - timedelta(days=1)
        now = timezone.now()
        delay_seconds = (reminder_time - now).total_seconds()
        if delay_seconds < 0:
            delay_seconds = 0

        # متن پیامک با تاریخ جلالی
        jalali_str = datetime2jalali(reservation_datetime).strftime("%Y/%m/%d %H:%M")
        message = f"سلام {user_name} ❤️\nیادآوری نوبت شما: {jalali_str}"

        send_sms_reminder.send_with_options(
            args=(phone_number, message, instance_id),
            delay=int(delay_seconds * 1000),
        )
        print("Task زمان‌بندی شد:", message)
    except Exception as e:
        print(f"⚠️ خطا در زمان‌بندی پیامک برای {phone_number}:", e)


@actor
def delete_expired_schedule(schedule_id):
    """حذف خودکار Schedule وقتی زمانش تموم شد"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        return  # از قبل پاک شده

    now = datetime.now()
    schedule_datetime = datetime.combine(schedule.date, schedule.end_time)

    # فقط اگه زمانش واقعاً گذشته بود
    if schedule_datetime <= now:
        schedule.delete()
        print(f"🗑️ Schedule {schedule_id} deleted automatically (expired).")
