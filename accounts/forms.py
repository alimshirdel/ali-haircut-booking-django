from django import forms
import re
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class ForgotPasswordRequestForm(forms.Form):
    identifier = forms.CharField(
        label="ایمیل یا شماره تلفن",
        widget=forms.TextInput(attrs={"placeholder": "ایمیل یا شماره تلفن"}),
    )

    def clean_identifier(self):
        val = self.cleaned_data["identifier"].strip()
        # می‌تونی تخصیص دهی بهتر (regex برای phone) انجام بدی
        if (
            not User.objects.filter(email__iexact=val).exists()
            and not User.objects.filter(phone_number__iexact=val).exists()
        ):
            raise ValidationError("کاربری با این ایمیل یا شماره پیدا نشد.")
        return val


class ForgotPasswordVerifyForm(forms.Form):
    opt = forms.CharField(
        label="کد تایید", widget=forms.TextInput(attrs={"placeholder": "کد تایید"})
    )
    password = forms.CharField(
        label="رمز جدید", widget=forms.PasswordInput(attrs={"placeholder": "رمز جدید"})
    )
    password_2 = forms.CharField(
        label="تکرار رمز جدید",
        widget=forms.PasswordInput(attrs={"placeholder": "تکرار رمز جدید"}),
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password_2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("رمزها یکسان نیستند.")
        # می‌تونی معیارهای قوی‌تر رمز (طول، نماد و ...) اضافه کنی
        return cleaned


class Login_form(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "نام کاربری خود را وارد کنید"}),
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "رمز خود را وارد کنید"}),
        required=True,
    )


class Register_form(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "نام"}), required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "نام خانوادگی"}), required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "نام کاربری"}), required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "ایمیل"}), required=True
    )
    phone = forms.CharField(
        widget=forms.NumberInput(attrs={"placeholder": "شماره موبایل"}), required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "رمز عبور"}), required=True
    )
    password_2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "تکرار رمز"}), required=True
    )
    opt = forms.CharField(
        widget=forms.NumberInput(attrs={"placeholder": "کد تایید"}), required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیستند.")
        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = re.sub(r"\D", "", phone)
            if len(phone) != 11 or not phone.startswith("09"):
                raise forms.ValidationError("شماره تلفن معتبر نیست. مثال: 09123456789")
        return phone
