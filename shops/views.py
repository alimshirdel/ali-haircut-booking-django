import requests, jdatetime
from persiantools import digits
from django.conf import settings
from django.db.models import Count
from django.db.models import FloatField , F
from django.db.models.functions import Sqrt, Power
from django.contrib import messages
from persiantools.jdatetime import JalaliDate
from django.contrib.auth import get_user_model
from .models import Shop, Schedule, Reservation, ShopComment, ShopRating
from datetime import timedelta, datetime, date
from .forms import CreateForm, EditForm, ScheduleForm, ShopCommentForm, ShopRatingForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

user = get_user_model()


@login_required
def create_view(request):
    if request.method == "POST":
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            shop_name = form.cleaned_data.get("name")
            shop_image = form.cleaned_data.get("image")
            shop_descriptions = form.cleaned_data.get("descriptions")
            shop_latitude = form.cleaned_data.get("latitude")
            shop_longitude = form.cleaned_data.get("longitude")
            shop_address = form.cleaned_data.get("address")
            shop_create_date = form.cleaned_data.get("create_date")
            shop_is_show = form.cleaned_data.get("is_show")
            Shop.objects.create(
                name=shop_name,
                image=shop_image,
                descriptions=shop_descriptions,
                address=shop_address,
                latitude=shop_latitude,
                longitude=shop_longitude,
                create_date=shop_create_date,
                is_show=shop_is_show,
                barber=request.user,
            )
            messages.success(request, "آرایشگاه با موفقیت ثبت شد!")
            return redirect("shops:shops_url")
    else:
        form = CreateForm()
    return render(request, "shops/create.html", {"form": form})


def shops_view(request):
    user_lat = request.GET.get("lat")
    user_lng = request.GET.get("lng")
    keyboard_search = request.GET.get("search")
    order = request.GET.get("order")
    shops = Shop.objects.filter(is_show=True)

    if keyboard_search:
        shops = shops.filter(name__icontains=keyboard_search)

    # مرتب‌سازی
    if order == "rating":
        # مرتب‌سازی بر اساس میانگین امتیاز (چون avg در مدل محاسبه میشه)
        shops = sorted(shops, key=lambda s: s.average_rating(), reverse=True)

    elif order == "price":
        # فرض کن مدل Shop فیلد price داره
        # shops = shops.order_by("price")
        pass

    elif order == "distance":
      # اگر مختصات کاربر موجود بود، فاصله رو حساب کن
      if user_lat and user_lng:
        user_lat = float(user_lat)
        user_lng = float(user_lng)

        shops = shops.annotate(
            distance=Sqrt(
                Power(F("latitude") - user_lat, 2) +
                Power(F("longitude") - user_lng, 2)
            )
        ).order_by("distance")

    elif order == "featured":
        # اگر مغازه‌های ویژه داری
        shops = shops.annotate(reservation_count=Count("schedules__reservations", distinct=True)).order_by("-reservation_count")

    paginator = Paginator(shops , 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "shops": page_obj,
        "search": keyboard_search,
        "order": order,
        }
    return render(request, "shops/shops.html", context)


MONTHS_FA = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}

WEEKDAYS_FA = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]


def move_jalali_month(year, month, delta):
    # delta = +1 for next, -1 for prev
    month += delta
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return year, month


def detail_view(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    schedules = shop.schedules.all().order_by("date", "start_time")

    # --- تعیین ماه/سال جلالی که باید نمایش داده شود ---
    jy = request.GET.get("jy")
    jm = request.GET.get("jm")
    if jy and jm:
        try:
            jy = int(jy)
            jm = int(jm)
        except ValueError:
            today_j = JalaliDate.today()
            jy, jm = today_j.year, today_j.month
    else:
        today_j = JalaliDate.today()
        jy, jm = today_j.year, today_j.month

    # --- اطلاعات اولیه درباره ماه ---
    j_first = JalaliDate(jy, jm, 1)
    # روز هفته شروع ماه (JalaliDate.weekday(): 0 = شنبه ... 6 = جمعه)
    start_weekday = j_first.weekday()

    # برای محاسبه تعداد روزهای ماه: از روز اول ماه بعد کم می‌کنیم
    if jm == 12:
        j_next_first = JalaliDate(jy + 1, 1, 1)
    else:
        j_next_first = JalaliDate(jy, jm + 1, 1)
    days_in_month = (j_next_first - j_first).days

    # مجموعه تاریخ‌های میلادی که برای این shop در schedules داریم (برای علامت‌گذاری)
    schedule_dates = set(
        s.date for s in schedules
    )  # schedules = shop.schedules.all() که قبلا گرفته‌ای

    # ساخت ماتریس 6x7
    weeks = []
    week = [None] * start_weekday  # خانه‌های خالی ابتدای ماه (اگر start_weekday>0)
    for d in range(1, days_in_month + 1):
        jday = JalaliDate(jy, jm, d)
        gday = jday.to_gregorian()  # datetime.date (میلادی)
        day_info = {
            "day": d,
            "day_fa": digits.en_to_fa(str(d)),
            "gregorian": gday,
            "gregorian_iso": gday.strftime("%Y-%m-%d"),
            "has_schedule": gday in schedule_dates,
            "is_today": gday == date.today(),
        }
        week.append(day_info)
        if len(week) == 7:
            weeks.append(week)
            week = []
    # پس از پایان، اگر هفته ناقص ماند، pad کن
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    # لینک‌های prev/next ماه (برای دکمه‌ها)
    prev_jy, prev_jm = move_jalali_month(jy, jm, -1)
    next_jy, next_jm = move_jalali_month(jy, jm, +1)

    schedule_slots = []
    for schedule in schedules:
        slots = []
        current_time = datetime.combine(schedule.date, schedule.start_time)
        end_time = datetime.combine(schedule.date, schedule.end_time)
        booked_slots = schedule.reservations.values_list("time_slot", flat=True)
        while current_time + timedelta(minutes=30) <= end_time:
            slot_time = current_time.time()
            slots.append({"time": slot_time, "booked": slot_time in booked_slots})
            current_time += timedelta(minutes=30)
        schedule_slots.append(
            {
                "date": schedule.date,
                "date_str": schedule.date.strftime("%Y-%m-%d"),  # اضافه شد
                "slots": slots,
                "schedule": schedule,
            }
        )
    # ======== بخش دیدگاه و امتیاز ========
    comments = shop.comments.all()
    comment_form = ShopCommentForm()
    rating_form = ShopRatingForm()
    avg = shop.average_rating()
    full_stars = int(avg)
    half_star = 1 if avg - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star


    if request.method == "POST":
        # ثبت دیدگاه
        if "comment_submit" in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "برای ارسال دیدگاه باید وارد شوید.")
                return redirect("shops:detail_url", pk)
            comment_form = ShopCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.shop = shop
                comment.save()
                messages.success(request, "دیدگاه شما ثبت شد.")
                return redirect("shops:detail_url", pk)

        # ثبت امتیاز
        elif "rating_submit" in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "برای ثبت امتیاز باید وارد شوید.")
                return redirect("shops:detail_url", pk)
            rating_form = ShopRatingForm(request.POST)
            if rating_form.is_valid():
                ShopRating.objects.update_or_create(
                    user=request.user,
                    shop=shop,
                    defaults={"value": rating_form.cleaned_data["value"]},
                )
                messages.success(request, "امتیاز شما ثبت شد.")
                return redirect("shops:detail_url", pk)
        elif "slot_time" in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "برای رزرو باید وارد سایت شوید.")
                return redirect("shops:detail_url", pk)
            else:
                slot_time_str = request.POST.get("slot_time")
                schedule_id = request.POST.get("schedule_id")
                schedule = Schedule.objects.get(id=schedule_id)
                slot_time = datetime.strptime(slot_time_str, "%H:%M").time()

            if schedule.reservations.filter(time_slot=slot_time).exists():
                messages.error(request, "این بازه زمانی قبلاً رزرو شده است.")
            else:
                Reservation.objects.create(
                    schedule=schedule, user=request.user, time_slot=slot_time
                )
                messages.success(request, "رزرو با موفقیت انجام شد.")

                end_slot_time = (
                    datetime.combine(schedule.date, slot_time) + timedelta(minutes=30)
                ).time()
                # ارسال پیامک به صاحب مغازه
                shop_owner_phone = schedule.shop.barber.phone_number
                if shop_owner_phone:
                    gregorian_date = schedule.date
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    jalali_str = f"{jalali_date.year}/{jalali_date.month:02}/{jalali_date.day:02}"
                    message = f"مشتری به نام {request.user.get_full_name()} ساعت {slot_time.strftime('%H:%M')} را تا ساعت {end_slot_time.strftime('%H:%M')} برای تاریخ {jalali_str} رزرو کرد."
                    send_sms(shop_owner_phone, message)
            return redirect("shops:detail_url", pk)
    # در view
    selected_date = request.GET.get("date")
    selected_slots = []
    for s in schedule_slots:
        if not selected_date or s["date_str"] == selected_date:
            # بررسی اینکه حداقل یک slot آزاد دارد
            free_slots = [slot for slot in s["slots"] if not slot["booked"]]
            if free_slots:
                selected_slots.append(s)

    context = {
        "shop": shop,
        "schedule_slots": schedule_slots,
        "calendar_weeks": weeks,
        "calendar_month_name": MONTHS_FA[jm],
        "calendar_year": digits.en_to_fa(str(jy)),
        "weekdays_fa": WEEKDAYS_FA,
        "prev_jy": prev_jy,
        "prev_jm": prev_jm,
        "next_jy": next_jy,
        "next_jm": next_jm,
        "selected_slots": selected_slots,
        # بخش دیدگاه و امتیاز:
        "comments": comments,
        "comment_form": comment_form,
        "rating_form": rating_form,
        "average_rating": avg,
        "full_stars": range(full_stars),
        "half_star": half_star,
        "empty_stars": range(empty_stars),
    }

    return render(request, "shops/detail.html", context)


def send_sms(shop_owner_phone, message):
    try:
        url = settings.MELIPAYAMAK_URL_SIMPLE  # در settings از .env خونده میشه
        payload = {
            "to": str(shop_owner_phone),
            "text": f"سلام ❤️\n{message}"
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        # سعی کن JSON بخونی، اگر JSON نبود raw text برگردون
        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        # بررسی موفقیت
        if response.ok:
            print("✅ SMS sent successfully:", data)
            return data
        else:
            print("❌ SMS failed:", data)
            return None

    except requests.Timeout:
        print("⏳ SMS Error: Request timed out")
        return None
    except requests.RequestException as e:
        print("⚠️ SMS Error:", e)
        return None


@login_required
def edit_view(request, pk):
    shop = get_object_or_404(Shop, pk=pk, barber=request.user)

    if request.method == "POST":
        form = EditForm(request.POST, request.FILES)
        if form.is_valid():
            shop.name = form.cleaned_data["name"]
            shop.descriptions = form.cleaned_data["descriptions"]
            shop.longitude = form.cleaned_data["longitude"]
            shop.latitude = form.cleaned_data["latitude"]
            if form.cleaned_data["image"]:
                shop.image = form.cleaned_data["image"]
            shop.create_date = form.cleaned_data["create_date"]
            shop.address = form.cleaned_data["address"]
            shop.is_show = form.cleaned_data["is_show"]
            shop.save()
            messages.success(request, "ویرایش با موفقیت انجام شد.")
            return redirect("shops:detail_url", pk=pk)
    else:
        form = EditForm(
            initial={
                "name": shop.name,
                "address": shop.address,
                "longitude": shop.longitude,
                "latitude": shop.latitude,
                "descriptions": shop.descriptions,
                "create_date": shop.create_date,
                "is_show": shop.is_show,
            }
        )

    return render(request, "shops/edit.html", {"form": form, "shop": shop})


@login_required
def delete_view(request, pk):
    shop = get_object_or_404(Shop, pk=pk, barber=request.user)
    shop.delete()
    return redirect("shops:shops_url")


@login_required
def reservation_create_view(request, pk):
    shop = get_object_or_404(Shop, pk=pk, barber=request.user)

    # فرم ارسال (POST)
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.shop = shop
            schedule.save()
            return redirect("shops:reservation_list_url", shop.id)
    else:
        form = ScheduleForm()

    # --- ساخت تقویم جلالی برای ماه مورد نظر (GET params: jy, jm) ---
    try:
        jy = int(request.GET.get("jy")) if request.GET.get("jy") else None
        jm = int(request.GET.get("jm")) if request.GET.get("jm") else None
    except ValueError:
        jy = jm = None

    today_j = JalaliDate.today()
    if not jy or not jm:
        jy, jm = today_j.year, today_j.month

    j_first = JalaliDate(jy, jm, 1)
    start_weekday = j_first.weekday()  # 0 = شنبه ... 6 = جمعه

    # تعداد روزهای ماه:
    if jm == 12:
        j_next_first = JalaliDate(jy + 1, 1, 1)
    else:
        j_next_first = JalaliDate(jy, jm + 1, 1)
    days_in_month = (j_next_first - j_first).days

    # تاریخ‌های موجود در schedule برای این shop (برای علامت‌گذاری)
    schedules = shop.schedules.all()
    schedule_dates = set(s.date for s in schedules)  # مجموعه datetime.date

    # ساخت هفته‌ها (لیست از لیست‌ها)
    weeks = []
    week = [None] * start_weekday
    for d in range(1, days_in_month + 1):
        jday = JalaliDate(jy, jm, d)
        gday = jday.to_gregorian()  # datetime.date
        day_info = {
            "day": d,
            "day_fa": digits.en_to_fa(str(d)),
            "gregorian": gday,
            "gregorian_iso": gday.strftime("%Y-%m-%d"),
            "has_schedule": gday in schedule_dates,
            "is_today": gday == date.today(),
        }
        week.append(day_info)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:  # تکمیل آخرین هفته
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    prev_jy, prev_jm = move_jalali_month(jy, jm, -1)
    next_jy, next_jm = move_jalali_month(jy, jm, +1)

    # اگر درخواست ajax برای بروزرسانی تقویم اومد، فقط partial تقویم رو برگردون
    context = {
        "form": form,
        "shop": shop,
        "calendar_weeks": weeks,
        "calendar_month_name": {
            1: "فروردین",
            2: "اردیبهشت",
            3: "خرداد",
            4: "تیر",
            5: "مرداد",
            6: "شهریور",
            7: "مهر",
            8: "آبان",
            9: "آذر",
            10: "دی",
            11: "بهمن",
            12: "اسفند",
        }[jm],
        "calendar_year": digits.en_to_fa(str(jy)),
        "weekdays_fa": [
            "شنبه",
            "یکشنبه",
            "دوشنبه",
            "سه‌شنبه",
            "چهارشنبه",
            "پنجشنبه",
            "جمعه",
        ],
        "prev_jy": prev_jy,
        "prev_jm": prev_jm,
        "next_jy": next_jy,
        "next_jm": next_jm,
        # اگر میخواهی روزی از قبل انتخاب شده باشد، میتوانی مقدار را از GET بگیری
        "selected_gregorian": request.GET.get("date", ""),
    }

    if request.GET.get("ajax") == "1":
        # فقط partial calendar — این فایل را در قدم بعدی ایجاد می‌کنیم
        return render(request, "shops/calendar.html", context)

    # صفحه کامل فرم ایجاد
    return render(request, "shops/reservation_create.html", context)


@login_required
def reservation_list_view(request, pk):
    shop = get_object_or_404(Shop, pk=pk, barber=request.user)
    schedules = shop.schedules.all().order_by("date", "start_time")
    return render(
        request, "shops/reservation_list.html", {"schedules": schedules, "shop": shop}
    )


@login_required
def reservation_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, shop__barber=request.user)
    pk = schedule.shop.pk
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "زمان با موفقیت حذف شد ✅")
    return redirect("shops:reservation_list_url", pk)


@login_required
def barber_reservations_view(request):
    reservations = (
        Reservation.objects.filter(schedule__shop__barber=request.user)
        .select_related("user", "schedule", "schedule__shop")
        .order_by("-time_slot")
    )
    return render(
        request, "shops/barber_reservations.html", {"reservations": reservations}
    )


@login_required
def my_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user).select_related(
        "schedule", "schedule__shop"
    )
    return render(request, "shops/my_reservations.html", {"reservations": reservations})


@login_required
def delete_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.delete()
    return redirect("shops:my_reservations_url")
