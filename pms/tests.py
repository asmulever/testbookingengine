from datetime import date, datetime, time, timedelta

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .models import Booking, Room, Room_type


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class MetricsAuditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        room_type = Room_type.objects.create(name="Simple", price=20, max_guests=1)
        cls.room = Room.objects.create(room_type=room_type, name="Room 3.1", description="Desc")
        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(days=1)
        cls.month_start = cls.today.replace(day=1)
        cls.prev_month_end = cls.month_start - timedelta(days=1)
        cls.prev_month_start = cls.prev_month_end.replace(day=1)

        cls._create_booking("NEW", 100, datetime.combine(cls.today, time(11, 0)), "MTA00001")
        cls._create_booking("DEL", 120, datetime.combine(cls.today, time(12, 0)), "MTA00002")
        cls._create_booking("NEW", 60, datetime.combine(cls.yesterday, time(10, 0)), "MTA00003")
        cls._create_booking("NEW", 40, datetime.combine(cls.prev_month_start + timedelta(days=2), time(10, 0)), "MTA00004")
        cls._create_booking("DEL", 35, datetime.combine(cls.prev_month_start + timedelta(days=3), time(10, 0)), "MTA00005")

    @classmethod
    def _create_booking(cls, state, total, created_at, code):
        booking = Booking.objects.create(
            state=state,
            checkin=created_at.date(),
            checkout=created_at.date() + timedelta(days=1),
            room=cls.room,
            guests=1,
            total=total,
            code=code,
        )
        Booking.objects.filter(id=booking.id).update(created=created_at)

    def test_metrics_audit_view_renders_and_contains_sections(self):
        response = self.client.get(reverse("metrics_audit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Métricas y Auditoría")
        self.assertContains(response, "Auditoría Diaria")
        self.assertContains(response, "Auditoría Mensual")
        self.assertContains(response, "Comparación Mensual")

    def test_metrics_audit_daily_metrics_values(self):
        response = self.client.get(reverse("metrics_audit"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["daily_current"]["created_count"], 2)
        self.assertEqual(response.context["daily_current"]["confirmed_count"], 1)
        self.assertEqual(response.context["daily_current"]["cancelled_count"], 1)
        self.assertEqual(response.context["daily_current"]["revenue"], 100.0)
        self.assertEqual(response.context["daily_previous"]["created_count"], 1)
        self.assertEqual(response.context["daily_previous"]["revenue"], 60.0)

    def test_metrics_audit_generates_expected_audit_rows(self):
        response = self.client.get(reverse("metrics_audit"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["daily_audit"]), 7)
        self.assertEqual(len(response.context["monthly_audit"]), 6)
