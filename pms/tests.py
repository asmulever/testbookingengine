from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from datetime import date, timedelta

from .models import Booking, Room, Room_type


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class RoomsFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        room_type = Room_type.objects.create(name="Simple", price=20, max_guests=1)
        Room.objects.create(room_type=room_type, name="Room 1.1", description="Desc")
        Room.objects.create(room_type=room_type, name="Room 1.2", description="Desc")
        Room.objects.create(room_type=room_type, name="Room 2.1", description="Desc")

    def test_rooms_page_without_filter_displays_all_rooms(self):
        response = self.client.get(reverse("rooms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Room 1.1")
        self.assertContains(response, "Room 1.2")
        self.assertContains(response, "Room 2.1")
        self.assertContains(response, "Total habitaciones: 3")

    def test_rooms_page_filters_by_partial_name(self):
        response = self.client.get(reverse("rooms"), {"name": "Room 1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resultados para <strong>"Room 1"</strong>: 2', html=True)
        self.assertContains(response, "Room 1.1")
        self.assertContains(response, "Room 1.2")
        self.assertNotContains(response, "Room 2.1")

    def test_rooms_page_shows_empty_state_when_no_matches(self):
        response = self.client.get(reverse("rooms"), {"name": "Suite"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se encontraron habitaciones para ese criterio.")


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class DashboardOccupancyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        room_type = Room_type.objects.create(name="Simple", price=20, max_guests=1)
        room_1 = Room.objects.create(room_type=room_type, name="Room 1.1", description="Desc")
        room_2 = Room.objects.create(room_type=room_type, name="Room 1.2", description="Desc")
        today = date.today()

        Booking.objects.create(
            state="NEW",
            checkin=today,
            checkout=today + timedelta(days=1),
            room=room_1,
            guests=1,
            total=20,
            code="CONF0001",
        )
        Booking.objects.create(
            state="DEL",
            checkin=today,
            checkout=today + timedelta(days=1),
            room=room_2,
            guests=1,
            total=20,
            code="CANC0001",
        )

    def test_dashboard_displays_occupancy_percentage_widget(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "% ocupación")
        self.assertContains(response, "50.00%")
        self.assertEqual(response.context["dashboard"]["occupancy_percentage"], 50.0)


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class DashboardOccupancyWithoutRoomsTests(TestCase):
    def test_dashboard_occupancy_is_zero_when_no_rooms_exist(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard"]["occupancy_percentage"], 0)
        self.assertContains(response, "0.00%")
