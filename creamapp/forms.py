"""
=============================================================================
  Glow & Care — Forms
=============================================================================
"""

from django import forms
from django.contrib.auth.models import User
from .models import Address, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone_number", "avatar"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 555 123 4567"}),
            "avatar":       forms.FileInput(attrs={"class": "form-control"}),
        }

class AddressForm(forms.ModelForm):
    """
    Used on the checkout page to save a new shipping address.
    The `user` FK is set in the view, not exposed in the form.
    """

    class Meta:
        model = Address
        fields = [
            "full_name",
            "phone",
            "street",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]
        widgets = {
            "full_name":   forms.TextInput(attrs={"placeholder": "Jane Doe"}),
            "phone":       forms.TextInput(attrs={"placeholder": "+1 555 000 0000"}),
            "street":      forms.TextInput(attrs={"placeholder": "123 Rose Street, Apt 4B"}),
            "city":        forms.TextInput(attrs={"placeholder": "Skopje"}),
            "state":       forms.TextInput(attrs={"placeholder": "Skopje Region"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "1000"}),
            "country":     forms.TextInput(attrs={"placeholder": "North Macedonia"}),
        }
        labels = {
            "is_default": "Save as my default address",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault("class", "form-control")
        self.fields["is_default"].widget.attrs["class"] = "form-check-input"
