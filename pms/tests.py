from datetime import date, timedelta

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .models import Booking, Room, Room_type


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class EditBookingDatesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        room_type = Room_type.objects.create(name="Simple", price=20, max_guests=1)
        cls.room = Room.objects.create(room_type=room_type, name="Room 1.1", description="Desc")
        cls.booking = Booking.objects.create(
            state="NEW",
            checkin=date.today() + timedelta(days=5),
            checkout=date.today() + timedelta(days=7),
            room=cls.room,
            guests=1,
            total=40,
            code="EDIT0001",
        )

    def test_edit_dates_view_updates_booking_when_room_is_available(self):
        response = self.client.post(
            reverse("edit_booking_dates", kwargs={"pk": self.booking.id}),
            data={
                "checkin": date.today() + timedelta(days=10),
                "checkout": date.today() + timedelta(days=12),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.checkin, date.today() + timedelta(days=10))
        self.assertEqual(self.booking.checkout, date.today() + timedelta(days=12))
        self.assertEqual(self.booking.total, 40)

    def test_edit_dates_view_renders_iso_values_for_date_inputs(self):
        response = self.client.get(reverse("edit_booking_dates", kwargs={"pk": self.booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.booking.checkin.strftime("%Y-%m-%d")}"')
        self.assertContains(response, f'value="{self.booking.checkout.strftime("%Y-%m-%d")}"')

    def test_edit_dates_view_displays_availability_error_when_dates_overlap(self):
        Booking.objects.create(
            state="NEW",
            checkin=date.today() + timedelta(days=8),
            checkout=date.today() + timedelta(days=11),
            room=self.room,
            guests=1,
            total=60,
            code="OVLP0001",
        )
        response = self.client.post(
            reverse("edit_booking_dates", kwargs={"pk": self.booking.id}),
            data={
                "checkin": date.today() + timedelta(days=9),
                "checkout": date.today() + timedelta(days=10),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay disponibilidad para las fechas seleccionadas")

    def test_edit_dates_view_displays_range_error_for_dates_after_2026_12_31(self):
        response = self.client.post(
            reverse("edit_booking_dates", kwargs={"pk": self.booking.id}),
            data={
                "checkin": date(2026, 12, 30),
                "checkout": date(2027, 1, 2),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solo se permiten reservas hasta el 31/12/2026")
