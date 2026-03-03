from datetime import date, timedelta

from django.db.models import F, Q, Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from .form_dates import Ymd
from .forms import *
from .models import Room
from .reservation_code import generate


class BookingSearchView(View):
    # renders search results for bookingings
    def get(self, request):
        query = request.GET.dict()
        if (not "filter" in query):
            return redirect("/")
        bookings = (Booking.objects
                    .filter(Q(code__icontains=query['filter']) | Q(customer__name__icontains=query['filter']))
                    .order_by("-created"))
        room_search_form = RoomSearchForm()
        context = {
            'bookings': bookings,
            'form': room_search_form,
            'filter': True
        }
        return render(request, "home.html", context)


class RoomSearchView(View):
    # renders the search form
    def get(self, request):
        room_search_form = RoomSearchForm()
        context = {
            'form': room_search_form
        }

        return render(request, "booking_search_form.html", context)

    # renders the search results of available rooms by date and guests
    def post(self, request):
        query = request.POST.dict()
        # calculate number of days in the hotel
        checkin = Ymd.Ymd(query['checkin'])
        checkout = Ymd.Ymd(query['checkout'])
        total_days = checkout - checkin
        # get available rooms and total according to dates and guests
        filters = {
            'room_type__max_guests__gte': query['guests']
        }
        exclude = {
            'booking__checkin__lte': query['checkout'],
            'booking__checkout__gte': query['checkin'],
            'booking__state__exact': "NEW"
        }
        rooms = (Room.objects
                 .filter(**filters)
                 .exclude(**exclude)
                 .annotate(total=total_days * F('room_type__price'))
                 .order_by("room_type__max_guests", "name")
                 )
        total_rooms = (Room.objects
                       .filter(**filters)
                       .values("room_type__name", "room_type")
                       .exclude(**exclude)
                       .annotate(total=Count('room_type'))
                       .order_by("room_type__max_guests"))
        # prepare context data for template
        data = {
            'total_days': total_days
        }
        # pass the actual url query to the template
        url_query = request.POST.urlencode()
        context = {
            "rooms": rooms,
            "total_rooms": total_rooms,
            "query": query,
            "url_query": url_query,
            "data": data
        }
        return render(request, "search.html", context)


class HomeView(View):
    # renders home page with all the bookingings order by date of creation
    def get(self, request):
        bookings = Booking.objects.all().order_by("-created")
        context = {
            'bookings': bookings
        }
        return render(request, "home.html", context)


class BookingView(View):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, pk):
        # check if customer form is ok
        customer_form = CustomerForm(request.POST, prefix="customer")
        if customer_form.is_valid():
            # save customer data
            customer = customer_form.save()
            # add the customer id to the booking form
            temp_POST = request.POST.copy()
            temp_POST.update({
                'booking-customer': customer.id,
                'booking-room': pk,
                'booking-code': generate.get()})
            # if ok, save booking data
            booking_form = BookingForm(temp_POST, prefix="booking")
            if booking_form.is_valid():
                booking_form.save()
        return redirect('/')

    def get(self, request, pk):
        # renders the form for booking confirmation.
        # It returns 2 forms, the one with the booking info is hidden
        # The second form is for the customer information

        query = request.GET.dict()
        room = Room.objects.get(id=pk)
        checkin = Ymd.Ymd(query['checkin'])
        checkout = Ymd.Ymd(query['checkout'])
        total_days = checkout - checkin
        total = total_days * room.room_type.price  # total amount to be paid
        query['total'] = total
        url_query = request.GET.urlencode()
        booking_form = BookingFormExcluded(prefix="booking", initial=query)
        customer_form = CustomerForm(prefix="customer")
        context = {
            "url_query": url_query,
            "room": room,
            "booking_form": booking_form,
            "customer_form": customer_form
        }
        return render(request, "booking.html", context)


class DeleteBookingView(View):
    # renders the booking deletion form
    def get(self, request, pk):
        booking = Booking.objects.get(id=pk)
        context = {
            'booking': booking
        }
        return render(request, "delete_booking.html", context)

    # deletes the booking
    def post(self, request, pk):
        Booking.objects.filter(id=pk).update(state="DEL")
        return redirect("/")


class EditBookingView(View):
    # renders the booking edition form
    def get(self, request, pk):
        booking = Booking.objects.get(id=pk)
        booking_form = BookingForm(prefix="booking", instance=booking)
        customer_form = CustomerForm(prefix="customer", instance=booking.customer)
        context = {
            'booking_form': booking_form,
            'customer_form': customer_form

        }
        return render(request, "edit_booking.html", context)

    # updates the customer form
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, pk):
        booking = Booking.objects.get(id=pk)
        customer_form = CustomerForm(request.POST, prefix="customer", instance=booking.customer)
        if customer_form.is_valid():
            customer_form.save()
            return redirect("/")


class DashboardView(View):
    def get(self, request):
        from datetime import date, time, datetime
        today = date.today()

        # get bookings created today
        today_min = datetime.combine(today, time.min)
        today_max = datetime.combine(today, time.max)
        today_range = (today_min, today_max)
        new_bookings = (Booking.objects
                        .filter(created__range=today_range)
                        .values("id")
                        ).count()

        # get incoming guests
        incoming = (Booking.objects
                    .filter(checkin=today)
                    .exclude(state="DEL")
                    .values("id")
                    ).count()

        # get outcoming guests
        outcoming = (Booking.objects
                     .filter(checkout=today)
                     .exclude(state="DEL")
                     .values("id")
                     ).count()

        # get outcoming guests
        invoiced = (Booking.objects
                    .filter(created__range=today_range)
                    .exclude(state="DEL")
                    .aggregate(Sum('total'))
                    )

        # preparing context data
        dashboard = {
            'new_bookings': new_bookings,
            'incoming_guests': incoming,
            'outcoming_guests': outcoming,
            'invoiced': invoiced

        }

        context = {
            'dashboard': dashboard
        }
        return render(request, "dashboard.html", context)


class RoomDetailsView(View):
    def get(self, request, pk):
        # renders room details
        room = Room.objects.get(id=pk)
        bookings = room.booking_set.all()
        context = {
            'room': room,
            'bookings': bookings}
        print(context)
        return render(request, "room_detail.html", context)


class RoomsView(View):
    def get(self, request):
        # renders a list of rooms
        rooms = Room.objects.all().values("name", "room_type__name", "id")
        context = {
            'rooms': rooms
        }
        return render(request, "rooms.html", context)


class MetricsAuditView(View):
    @staticmethod
    def _period_metrics(start_date, end_date):
        bookings = Booking.objects.filter(created__date__gte=start_date, created__date__lte=end_date)
        confirmed = bookings.exclude(state="DEL")
        return {
            "created_count": bookings.count(),
            "confirmed_count": confirmed.count(),
            "cancelled_count": bookings.filter(state="DEL").count(),
            "revenue": float(confirmed.aggregate(total=Sum("total"))["total"] or 0),
        }

    @staticmethod
    def _comparison(current, previous):
        delta = current - previous
        if previous == 0:
            percent = 0 if current == 0 else 100
        else:
            percent = (delta / previous) * 100
        direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
        return {
            "delta": delta,
            "percent": percent,
            "direction": direction,
        }

    def get(self, request):
        today = date.today()
        yesterday = today - timedelta(days=1)
        month_start = today.replace(day=1)
        previous_month_end = month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)

        daily_current = self._period_metrics(today, today)
        daily_previous = self._period_metrics(yesterday, yesterday)
        monthly_current = self._period_metrics(month_start, today)
        monthly_previous = self._period_metrics(previous_month_start, previous_month_end)

        daily_comparison = {
            "created_count": self._comparison(daily_current["created_count"], daily_previous["created_count"]),
            "confirmed_count": self._comparison(daily_current["confirmed_count"], daily_previous["confirmed_count"]),
            "cancelled_count": self._comparison(daily_current["cancelled_count"], daily_previous["cancelled_count"]),
            "revenue": self._comparison(daily_current["revenue"], daily_previous["revenue"]),
        }
        monthly_comparison = {
            "created_count": self._comparison(monthly_current["created_count"], monthly_previous["created_count"]),
            "confirmed_count": self._comparison(monthly_current["confirmed_count"], monthly_previous["confirmed_count"]),
            "cancelled_count": self._comparison(monthly_current["cancelled_count"], monthly_previous["cancelled_count"]),
            "revenue": self._comparison(monthly_current["revenue"], monthly_previous["revenue"]),
        }

        last_7_days_start = today - timedelta(days=6)
        raw_daily = (Booking.objects
                     .filter(created__date__gte=last_7_days_start, created__date__lte=today)
                     .annotate(period=TruncDate("created"))
                     .values("period")
                     .annotate(
                         created_count=Count("id"),
                         cancelled_count=Count("id", filter=Q(state="DEL")),
                         revenue=Sum("total", filter=~Q(state="DEL")),
                     )
                     .order_by("period"))
        daily_map = {entry["period"]: entry for entry in raw_daily}
        daily_audit = []
        for day_offset in range(6, -1, -1):
            day = today - timedelta(days=day_offset)
            entry = daily_map.get(day, {})
            daily_audit.append({
                "label": day.strftime("%d/%m"),
                "created_count": entry.get("created_count", 0),
                "cancelled_count": entry.get("cancelled_count", 0),
                "revenue": float(entry.get("revenue") or 0),
            })

        month_cursor = month_start
        for _ in range(5):
            month_cursor = (month_cursor - timedelta(days=1)).replace(day=1)
        raw_monthly = (Booking.objects
                       .filter(created__date__gte=month_cursor, created__date__lte=today)
                       .annotate(period=TruncMonth("created"))
                       .values("period")
                       .annotate(
                           created_count=Count("id"),
                           cancelled_count=Count("id", filter=Q(state="DEL")),
                           revenue=Sum("total", filter=~Q(state="DEL")),
                       )
                       .order_by("period"))
        monthly_map = {
            (entry["period"].year, entry["period"].month): entry for entry in raw_monthly
        }
        monthly_audit = []
        month_iter = month_cursor
        for _ in range(6):
            key = (month_iter.year, month_iter.month)
            entry = monthly_map.get(key, {})
            monthly_audit.append({
                "label": month_iter.strftime("%b %Y"),
                "created_count": entry.get("created_count", 0),
                "cancelled_count": entry.get("cancelled_count", 0),
                "revenue": float(entry.get("revenue") or 0),
            })
            month_iter = (month_iter + timedelta(days=32)).replace(day=1)

        daily_max_created = max((item["created_count"] for item in daily_audit), default=0)
        daily_max_revenue = max((item["revenue"] for item in daily_audit), default=0)
        for item in daily_audit:
            item["created_pct"] = 0 if daily_max_created == 0 else int((item["created_count"] / daily_max_created) * 100)
            item["revenue_pct"] = 0 if daily_max_revenue == 0 else int((item["revenue"] / daily_max_revenue) * 100)

        monthly_max_created = max((item["created_count"] for item in monthly_audit), default=0)
        monthly_max_revenue = max((item["revenue"] for item in monthly_audit), default=0)
        for item in monthly_audit:
            item["created_pct"] = 0 if monthly_max_created == 0 else int((item["created_count"] / monthly_max_created) * 100)
            item["revenue_pct"] = 0 if monthly_max_revenue == 0 else int((item["revenue"] / monthly_max_revenue) * 100)

        total_daily_created = sum(item["created_count"] for item in daily_audit)
        total_daily_cancelled = sum(item["cancelled_count"] for item in daily_audit)
        total_daily_revenue = sum(item["revenue"] for item in daily_audit)
        total_monthly_created = sum(item["created_count"] for item in monthly_audit)
        total_monthly_cancelled = sum(item["cancelled_count"] for item in monthly_audit)
        total_monthly_revenue = sum(item["revenue"] for item in monthly_audit)

        daily_cancellation_rate = 0 if total_daily_created == 0 else (total_daily_cancelled / total_daily_created) * 100
        monthly_cancellation_rate = 0 if total_monthly_created == 0 else (total_monthly_cancelled / total_monthly_created) * 100
        daily_avg_ticket = 0 if daily_current["confirmed_count"] == 0 else daily_current["revenue"] / daily_current["confirmed_count"]
        monthly_avg_ticket = 0 if monthly_current["confirmed_count"] == 0 else monthly_current["revenue"] / monthly_current["confirmed_count"]

        peak_day = max(daily_audit, key=lambda x: x["revenue"], default={"label": "-", "revenue": 0})
        peak_month = max(monthly_audit, key=lambda x: x["revenue"], default={"label": "-", "revenue": 0})

        context = {
            "daily_current": daily_current,
            "daily_previous": daily_previous,
            "monthly_current": monthly_current,
            "monthly_previous": monthly_previous,
            "daily_comparison": daily_comparison,
            "monthly_comparison": monthly_comparison,
            "daily_audit": daily_audit,
            "monthly_audit": monthly_audit,
            "daily_cancellation_rate": daily_cancellation_rate,
            "monthly_cancellation_rate": monthly_cancellation_rate,
            "daily_avg_ticket": daily_avg_ticket,
            "monthly_avg_ticket": monthly_avg_ticket,
            "total_daily_revenue": total_daily_revenue,
            "total_monthly_revenue": total_monthly_revenue,
            "peak_day": peak_day,
            "peak_month": peak_month,
            "today": today,
        }
        return render(request, "metrics_audit.html", context)
