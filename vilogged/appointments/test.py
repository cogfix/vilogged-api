from django.test import TestCase
from .models import Appointments, AppointmentLogs
from vilogged.users.models import UserProfile
from vilogged.visitors.models import VisitorGroup, Visitors


class AppointmentsTestCase(TestCase):
    user = dict()
    visitor = dict()

    def setUp(self):
        super(AppointmentsTestCase, self).setUp()

        self.user = UserProfile.objects.create(
            username='admin1234',
            email='admin@admin.com',
            password='12345',
            phone='080666676676'
        )

        self.visitor = Visitors.objects.create(
            last_name='Visitor1',
            first_name='Visitor1',
            email='visitor@mail.com',
            phone='080666676676'
        )

        Appointments.objects.create(
            host=self.user,
            visitor=self.visitor,
            start_time='10:30:12',
            end_time='11:30:12',
            start_date='2016-12-12',
            end_date='2016-12-12'
        )

    def test_appointment(self):
        event = Appointments.objects.all().first()
        self.assertEqual(event.host, self.user)
        self.assertEqual(event.visitor, self.visitor)

    def test_appointment_to_json(self):
        data = Appointments.objects.get(host=self.user)
        json_data = data.to_json(True)
        self.assertEqual(json_data.get('host', None).get('username'), self.user.to_json().get('username'))
        self.assertEqual(json_data.get('visitor', None).get('first_name'), self.visitor.to_json().get('first_name'))


