from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
import random, time, requests
from .forms import (
    Login_form,
    Register_form,
    ForgotPasswordRequestForm,
    ForgotPasswordVerifyForm,
)
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect("shops:shops_url")

    form = Register_form(request.POST or None)
    otp_stage = bool(request.session.get("verification_code"))
    remaining_time = 0

    if otp_stage:
        expire = request.session.get("verification_expire")
        if expire:
            remaining_time = int(max(0, expire - time.time()))

    if request.method == "POST":
        # چک ارسال مجدد
        if request.POST.get("resend") == "1" and otp_stage:
            phone = request.session.get("user_phone")
            if phone:


                code = send_sms(phone)
                request.session["verification_code"] = code
                request.session["verification_expire"] = time.time() + 300  # ۵ دقیقه
                request.session.modified = True
                messages.success(request, "کد تایید دوباره ارسال شد.")
                remaining_time = 300  # ریست تایمر
            return render(
                request,
                "accounts/register.html",
                {
                    "form": form,
                    "otp_stage": otp_stage,
                    "remaining_time": remaining_time,
                },
            )

        if otp_stage:  # مرحله دوم: تایید OTP
            entered_otp = request.POST.get("opt")
            saved_code = request.session.get("verification_code")
            expire = request.session.get("verification_expire")
            data = request.session.get("user_data")
            phone = request.session.get("user_phone")

            if not saved_code or not data:
                messages.error(request, "مهلت کد تمام شده یا اطلاعات ثبت‌نام ناقص است.")
            elif time.time() > expire:
                messages.error(request, "کد منقضی شده، دوباره تلاش کنید.")
            elif str(saved_code) != str(entered_otp):
                messages.error(request, "کد تایید نادرست است.")
            else:
                if User.objects.filter(username=data["username"]).exists():
                    messages.error(request, "این نام کاربری قبلا ثبت شده است.")
                elif User.objects.filter(phone_number=phone).exists():
                    messages.error(request, "این شماره موبایل قبلا ثبت شده است.")
                else:
                    user = User.objects.create_user(
                        username=data["username"],
                        password=data["password"],
                        email=data["email"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                    )
                    user.phone_number = phone
                    user.save()
                    login(request, user)
                    messages.success(request, "ثبت‌نام موفقیت‌آمیز بود ✅")
                    # پاک کردن سشن OTP
                    for key in [
                        "verification_code",
                        "verification_expire",
                        "user_data",
                        "user_phone",
                    ]:
                        request.session.pop(key, None)
                    return render(
                        request,
                        "accounts/register.html",
                        {"form": form, "redirect": True},
                    )

        else:  # مرحله اول
            if form.is_valid():
                username = form.cleaned_data["username"]
                phone = form.cleaned_data["phone"]

                if User.objects.filter(username=username).exists():
                    messages.error(request, "این نام کاربری قبلا ثبت شده است.")
                elif User.objects.filter(phone_number=phone).exists():
                    messages.error(request, "این شماره موبایل قبلا ثبت شده است.")
                else:
                    data = {
                        "username": username,
                        "password": form.cleaned_data["password"],
                        "email": form.cleaned_data["email"],
                        "first_name": form.cleaned_data["first_name"],
                        "last_name": form.cleaned_data["last_name"],
                    }


                    code = send_sms(phone)
                    request.session["verification_code"] = code
                    request.session["verification_expire"] = time.time() + 300
                    request.session["user_data"] = data
                    request.session["user_phone"] = phone

                    messages.info(request, "کد تایید برای شما ارسال شد.")
                    remaining_time = 300
                    otp_stage = True
            else:
                messages.error(request, "اطلاعات وارد شده معتبر نیست.")

    return render(
        request,
        "accounts/register.html",
        {"form": form, "otp_stage": otp_stage, "remaining_time": remaining_time},
    )



def send_sms(phone):
    try:
        url = settings.MELIPAYAMAK_URL
        payload = {"to": str(phone)}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # اگر خطای HTTP وجود داشته باشد، Exception می‌اندازد

        data = response.json()  # پاسخ JSON از ملی پیامک
        print("📨 Response from MeliPayamak:", data)

        # اگر پاسخ شامل کد OTP است، آن را استخراج کن
        result = data.get("result") or data
        code = None
        if isinstance(result, dict):
            code = result.get("code") or result.get("otp")

        if code:
            print("✅ OTP sent successfully:", code)
        else:
            print("⚠️ OTP sent but no code returned")

        return code

    except requests.RequestException as e:
        print("❌ SMS sending failed:", e)
        return None



def login_view(request):
    next = request.GET.get("next")
    if request.user.is_authenticated:
        return redirect("shops:shops_url")
    if request.method == "GET":
        form = Login_form()
        return render(request, "accounts/login.html", {"form": form})
    else:
        form = Login_form(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data.get("username")
            form_password = form.cleaned_data.get("password")
            user = authenticate(username=form_username, password=form_password)

            if user is not None:
                login(request, user)
                if next:
                    return redirect(next)
                else:
                    messages.success(
                        request, "ورود موفقیت‌آمیز بود! در حال انتقال به صفحه اصلی…"
                    )
                    # در این حالت هنوز ریدایرکت نکردیم
                    return render(
                        request, "accounts/login.html", {"form": form, "redirect": True}
                    )
            else:
                messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
                return render(request, "accounts/login.html", {"form": form})
        else:
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
            return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("shops:shops_url")


OTP_SESSION_KEY = "forgot_password_otp"
OTP_SESSION_EXPIRES = 5 * 60  # 5 دقیقه


@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect("shops:shops_url")

    otp_data = request.session.get(OTP_SESSION_KEY)
    remaining_time = 0
    re_create = request.POST.get("resend") == "1"
    identifier = request.POST.get("identifier") or (
        otp_data.get("identifier") if otp_data else None
    )

    # بررسی انقضا
    if otp_data:
        remaining_time = int(max(0, otp_data.get("expires_at", 0) - time.time()))
        if remaining_time == 0:
            del request.session[OTP_SESSION_KEY]
            otp_data = None
            messages.error(request, "کد تایید منقضی شد. دوباره تلاش کنید.")
            # اگر کاربر روی resend کلیک کرده → OTP جدید بساز
            if re_create and identifier:
                code = f"{random.randint(1000, 9999)}"
                expires_at = time.time() + OTP_SESSION_EXPIRES
                request.session[OTP_SESSION_KEY] = {
                    "code": code,
                    "identifier": identifier,
                    "expires_at": expires_at,
                }
                request.session.modified = True
                user = (
                    User.objects.filter(email__iexact=identifier).first()
                    or User.objects.filter(phone_number__iexact=identifier).first()
                )
                send_otp_to_user(
                    identifier,
                    code,
                    username=user.username if "user" in locals() else None,
                )
                messages.success(request, "کد تایید برای شما ارسال شد.")
                remaining_time = 5 * 60
                otp_data = request.session.get(OTP_SESSION_KEY)

    if otp_data:
        # مرحله دوم
        form = ForgotPasswordVerifyForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            entered = form.cleaned_data["opt"].strip()
            if entered == otp_data.get("code"):
                ident = otp_data.get("identifier")
                user_qs = User.objects.filter(email__iexact=ident)
                if not user_qs.exists():
                    user_qs = User.objects.filter(phone_number__iexact=ident)
                user = user_qs.first()
                if user:
                    user.set_password(form.cleaned_data["password"])
                    user.save()
                    del request.session[OTP_SESSION_KEY]
                    messages.success(
                        request, "رمز با موفقیت تغییر کرد. حالا وارد شوید."
                    )
                    return redirect("accounts:login_url")
                else:
                    messages.error(request, "کاربر پیدا نشد.")
            else:
                messages.error(request, "کد تایید اشتباه است.")
        return render(
            request,
            "accounts/forgot_password.html",
            {
                "form": form,
                "step": 2,
                "remaining_time": remaining_time,
                "otp_data": otp_data,
            },
        )

    # مرحله اول
    form = ForgotPasswordRequestForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            identifier = form.cleaned_data["identifier"].strip()

            # پیدا کردن کاربر
            user = (
                User.objects.filter(email__iexact=identifier).first()
                or User.objects.filter(phone_number__iexact=identifier).first()
            )
            if not user:
                messages.error(request, "کاربری با این ایمیل یا شماره پیدا نشد.")
                return render(
                    request, "accounts/forgot_password.html", {"form": form, "step": 1}
                )
            code = f"{random.randint(1000, 9999)}"
            expires_at = time.time() + OTP_SESSION_EXPIRES
            request.session[OTP_SESSION_KEY] = {
                "code": code,
                "identifier": identifier,
                "expires_at": expires_at,
            }
            request.session.modified = True

            send_otp_to_user(identifier, code, username=user.username)

            messages.success(request, "کد تایید برای شما ارسال شد.")
            return redirect("accounts:forgot_password_url")
        else:
            messages.error(request, "شماره تلفن یا ایمیل نامعتبر است.")
            return render(
                request, "accounts/forgot_password.html", {"form": form, "step": 1}
            )
    return render(request, "accounts/forgot_password.html", {"form": form, "step": 1})


def send_otp_to_user(identifier, code, username=None):
    if "@" in identifier and "." in identifier:
        # ایمیل
        subject = "کد تایید بازیابی رمز و نام کاربری سایت موکات❤️ "
        message = f"کد تایید شما: {code}\nاین کد تا ۵ دقیقه معتبر است❤️.\nنام کاربری شما🌹: {username}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient = [identifier]
        send_mail(subject, message, from_email, recipient, fail_silently=False)
    else:

        try:
            url = settings.MELIPAYAMAK_URL  # از settings یا env می‌گیری
            payload = {
                "bodyId": 376148,  # همون قالبی که در ملی‌پیامک ساختی
                "to": str(identifier),
                "args": [str(code), username or ""],
            }
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json() if response.content else {}

            # بررسی موفقیت پاسخ
            if response.ok and data.get("status") != "error":
                print("✅ SMS sent:", data)
                return True
            else:
                print("❌ SMS error:", data)
                return False

        except requests.Timeout:
            print("⏳ SMS Error: Timeout")
            return False
        except requests.RequestException as e:
            print("⚠️ SMS Error:", e)
            return False