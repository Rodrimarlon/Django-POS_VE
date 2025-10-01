from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Username"),
                "class": "form-control form-control-user"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
                "class": "form-control form-control-user"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Username"),
                "class": "form-control"
            }
        ),
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={
            'unique': _("A user with that username already exists."),
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("Email"),
                "class": "form-control"
            }
        ),
        error_messages={
            'invalid': _("Enter a valid email address."),
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
                "class": "form-control"
            }
        ),
        label=_("Password")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password confirmation"),
                "class": "form-control"
            }
        ),
        label=_("Password confirmation")
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_password2(self):
        password_1 = self.cleaned_data.get("password1")
        password_2 = self.cleaned_data.get("password2")
        if password_1 and password_2 and password_1 != password_2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password_2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
