from datetime import date, datetime
from django import forms
from django.forms import ModelForm

from .models import Booking, Customer


class RoomSearchForm(ModelForm):
    class Meta:
        model = Booking
        fields = ['checkin', 'checkout', 'guests']
        labels = {
            "guests": "Huéspedes"
        }
        widgets = {
            'checkin': forms.DateInput(attrs={'type': 'date', 'min': datetime.today().strftime('%Y-%m-%d')}),
            'checkout': forms.DateInput(
                attrs={'type': 'date', 'max': datetime.today().replace(month=12, day=31).strftime('%Y-%m-%d')}),
            'guests': forms.DateInput(attrs={'type': 'number', 'min': 1, 'max': 4}),
        }


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        labels = {
            "name": "Nombre y apellido",
            "phone": "Teléfono"
        }


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        labels = {
        }
        widgets = {
            'checkin': forms.HiddenInput(),
            'checkout': forms.HiddenInput(),
            'guests': forms.HiddenInput()
        }


class BookingFormExcluded(ModelForm):
    class Meta:
        model = Booking
        exclude = ["customer", "room", "code"]
        labels = {
        }
        widgets = {
            'checkin': forms.HiddenInput(),
            'checkout': forms.HiddenInput(),
            'guests': forms.HiddenInput(),
            'total': forms.HiddenInput(),
            'state': forms.HiddenInput(),
        }


class RoomFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label="Buscar habitación",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej: Room 1",
                "class": "form-control rooms-filter-input",
                "autocomplete": "off",
            }
        ),
    )


class BookingDatesEditForm(forms.Form):
    checkin = forms.DateField(
        label="Fecha de entrada",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "max": date(2026, 12, 31).strftime("%Y-%m-%d"),
                "class": "form-control",
            }
        ),
    )
    checkout = forms.DateField(
        label="Fecha de salida",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "max": date(2026, 12, 31).strftime("%Y-%m-%d"),
                "class": "form-control",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        checkin = cleaned_data.get("checkin")
        checkout = cleaned_data.get("checkout")
        if not checkin or not checkout:
            return cleaned_data

        if checkout <= checkin:
            raise forms.ValidationError("La fecha de salida debe ser posterior a la fecha de entrada")

        max_allowed_date = date(2026, 12, 31)
        if checkin > max_allowed_date or checkout > max_allowed_date:
            raise forms.ValidationError("Solo se permiten reservas hasta el 31/12/2026")

        return cleaned_data
