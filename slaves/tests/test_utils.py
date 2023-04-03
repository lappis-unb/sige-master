from requests.models import Response
from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from rest_framework import status
from unittest import mock

from slaves.api import request_all_events
from slaves.utils import DataCollector
from slaves.models import Slave
from measurements.models import EnergyTransductor
from campi.models import Campus
from events.models import FailedConnectionTransductorEvent
from events.models import CriticalVoltageEvent
from events.models import PrecariousVoltageEvent
from events.models import PhaseDropEvent


def get_event_response(event_type: str, created_at: str, ended_at: str = None):
    events_response = Response()
    events_response._content = f'''
    [
        {{
            "type": "{event_type}",
            "ip_address": "192.168.1.1",
            "created_at": "{created_at}",
            "ended_at": {'null' if ended_at is None else f'"{ended_at}"'},
            "data": {{
                "voltage_a": 228.8789520263672,
                "voltage_b": 228.71775817871094,
                "voltage_c": 228.47679138183594
            }}
        }}
    ]
    '''

    return [
        (
            'Event',
            events_response
        )
    ]


def get_several_events_in_different_states_response():
    failed_conn_event_response = Response()
    voltage_related_event_response = Response()

    failed_conn_event_response._content = '''
        [
            {
                "type": "FailedConnectionTransductorEvent",
                "ip_address": "192.168.1.1",
                "created_at": "2021-03-08T16:04:03",
                "ended_at": "2021-03-08T16:05:04",
                "data": {
                }
            }
        ]
        '''

    voltage_related_event_response._content = '''
    [
        {
            "type": "CriticalVoltageEvent",
            "ip_address": "192.168.1.1",
            "created_at": "2021-03-08T16:04:03",
            "ended_at": null,
            "data": {
            }
        },
        {
            "type": "PrecariousVoltageEvent",
            "ip_address": "192.168.1.1",
            "created_at": "2021-03-08T18:04:03",
            "ended_at": null,
            "data": {
            }
        },
        {
            "type": "PhaseDropEvent",
            "ip_address": "192.168.1.1",
            "created_at": "2021-03-08T16:04:03",
            "ended_at": null,
            "data": {
            }
        }
    ]
    '''

    return [
        (
            'FailedConnectionTransductorEvent',
            failed_conn_event_response
        ),
        (
            'VoltageRelatedEvent',
            voltage_related_event_response
        )
    ]


class GetEventsFromTransductorsTestCase(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(
            name='UnB - Faculdade Gama',
            acronym='FGA',
        )

        self.slave = Slave.objects.create(
            ip_address="1.1.1.1",
            name="UED FGA",
            broken=False
        )

        self.energy_transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='192.168.1.1',
            geolocation_latitude=20.1,
            geolocation_longitude=37.9,
            name="MESP 1",
            broken=True,
            active=False,
            creation_date=timezone.now(),
            firmware_version='0.1',
            model='EnergyTransductorModel',
            campus=self.campus
        )

        self.slave.transductors.add(self.energy_transductor)

    @mock.patch('slaves.utils.request_all_events',
                return_value=get_event_response(
                    "FailedConnectionTransductorEvent", "2021-03-08T16:04:03"))
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_start_failed_connection_event(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()

        failed_events = list(FailedConnectionTransductorEvent.objects.all())

        self.assertEqual(1, len(failed_events))
        self.assertEqual(self.energy_transductor, failed_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         failed_events[0].created_at)
        self.assertEqual(None, failed_events[0].ended_at)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "FailedConnectionTransductorEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "FailedConnectionTransductorEvent",
                "2021-03-08T16:04:03",
                "2021-03-08T16:05:03")
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_finish_failed_connection_event(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()
        DataCollector.get_events()

        failed_events = list(FailedConnectionTransductorEvent.objects.all())
        start_event = failed_events[0].created_at
        end_event = failed_events[0].ended_at
        event_interval = end_event - start_event

        self.assertEqual(1, len(failed_events))
        self.assertEqual(self.energy_transductor, failed_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         start_event)
        self.assertEqual(datetime(2021, 3, 8, 16, 5, 3),
                         end_event)
        self.assertEqual(60, event_interval.seconds)

    @mock.patch('slaves.utils.request_all_events',
                return_value=get_event_response(
                    "CriticalVoltageEvent", "2021-03-08T16:04:03"))
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_start_critical_voltage_event(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()

        critical_volt_events = list(CriticalVoltageEvent.objects.all())

        self.assertEqual(1, len(critical_volt_events))
        self.assertEqual(self.energy_transductor,
                         critical_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         critical_volt_events[0].created_at)
        self.assertEqual(None, critical_volt_events[0].ended_at)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "CriticalVoltageEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "CriticalVoltageEvent",
                "2021-03-08T16:04:03",
                "2021-03-08T17:04:03")
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_finish_critical_voltage_event_interval_1_hour(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()
        DataCollector.get_events()

        critical_volt_events = list(CriticalVoltageEvent.objects.all())
        start_event = critical_volt_events[0].created_at
        end_event = critical_volt_events[0].ended_at
        event_interval = end_event - start_event

        self.assertEqual(1, len(critical_volt_events))
        self.assertEqual(self.energy_transductor,
                         critical_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         start_event)
        self.assertEqual(datetime(2021, 3, 8, 17, 4, 3),
                         end_event)
        self.assertEqual(3600, event_interval.seconds)

    @mock.patch('slaves.utils.request_all_events',
                return_value=get_event_response(
                    "PrecariousVoltageEvent", "2021-03-08T16:04:03"))
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_start_precarious_voltage_event(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()

        precarious_volt_events = list(PrecariousVoltageEvent.objects.all())

        self.assertEqual(1, len(precarious_volt_events))
        self.assertEqual(self.energy_transductor,
                         precarious_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         precarious_volt_events[0].created_at)
        self.assertEqual(None, precarious_volt_events[0].ended_at)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "PrecariousVoltageEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "PrecariousVoltageEvent", "2021-03-08T16:04:03")
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_update_precarious_voltage_event_without_end_date(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()
        DataCollector.get_events()

        precarious_volt_events = list(PrecariousVoltageEvent.objects.all())
        start_event = precarious_volt_events[0].created_at
        end_event = precarious_volt_events[0].ended_at

        self.assertEqual(1, len(precarious_volt_events))
        self.assertEqual(self.energy_transductor,
                         precarious_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         start_event)
        self.assertEqual(None, precarious_volt_events[0].ended_at)

    @mock.patch('slaves.utils.request_all_events',
                return_value=get_event_response(
                    "PhaseDropEvent", "2021-03-08T16:04:03"))
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_start_phase_drop_event(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()

        phase_drop_events = list(PhaseDropEvent.objects.all())

        self.assertEqual(1, len(phase_drop_events))
        self.assertEqual(self.energy_transductor,
                         phase_drop_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         phase_drop_events[0].created_at)
        self.assertEqual(None, phase_drop_events[0].ended_at)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "PhaseDropEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "PhaseDropEvent", "2021-03-08T17:04:03"),
            get_event_response(
                "PhaseDropEvent", "2021-03-08T17:04:03", "2021-03-08T18:05:05")
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_update_and_finish_phase_drop_event_interval_2_hours(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()  # start event
        DataCollector.get_events()  # update event
        DataCollector.get_events()  # finish event

        phase_drop_events = list(PhaseDropEvent.objects.all())
        start_event = phase_drop_events[0].created_at
        end_event = phase_drop_events[0].ended_at
        event_interval = end_event - start_event

        self.assertEqual(1, len(phase_drop_events))
        self.assertEqual(self.energy_transductor,
                         phase_drop_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         start_event)
        self.assertEqual(datetime(2021, 3, 8, 18, 5, 5),
                         end_event)
        self.assertEqual(7262, event_interval.seconds)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "PhaseDropEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "PhaseDropEvent", "2021-03-08T16:04:03", "2021-03-08T17:04:05"),
            get_event_response(
                "PhaseDropEvent", "2021-03-08T18:05:05")
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_create_two_phase_drop_events(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()  # start event 1
        DataCollector.get_events()  # finish event 1
        DataCollector.get_events()  # start event 2

        phase_drop_events = list(PhaseDropEvent.objects.all())
        start_event_1 = phase_drop_events[0].created_at
        start_event_2 = phase_drop_events[1].created_at
        end_event_1 = phase_drop_events[0].ended_at
        end_event_2 = phase_drop_events[1].ended_at
        event_1_interval = end_event_1 - start_event_1

        self.assertEqual(2, len(phase_drop_events))
        self.assertEqual(self.energy_transductor,
                         phase_drop_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         start_event_1)
        self.assertEqual(datetime(2021, 3, 8, 17, 4, 5),
                         end_event_1)
        self.assertEqual(3602, event_1_interval.seconds)
        self.assertEqual(datetime(2021, 3, 8, 18, 5, 5), start_event_2)
        self.assertEqual(None, end_event_2)

    @mock.patch(
        'slaves.utils.request_all_events',
        side_effect=[
            get_event_response(
                "FailedConnectionTransductorEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "CriticalVoltageEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "PrecariousVoltageEvent", "2021-03-08T16:04:03"),
            get_event_response(
                "PrecariousVoltageEvent", "2021-03-08T16:10:03"),
            get_event_response(
                "PrecariousVoltageEvent",
                "2021-03-08T16:04:03",
                "2021-03-08T17:04:03"),
            get_several_events_in_different_states_response()
        ]
    )
    @mock.patch('events.models.fcm_send_topic_message', return_value=None)
    def test_several_events_on_same_transductor(
            self, mock_events_request, mock_topic_message):
        DataCollector.get_events()  # start failed connection event
        DataCollector.get_events()  # start critical voltage event
        DataCollector.get_events()  # start precarious voltage event 1
        DataCollector.get_events()  # update precarious voltage event 1
        DataCollector.get_events()  # finish precarious voltage event 1
        # start phase drop, start precarious 2,
        # update critical, finish failed conn
        DataCollector.get_events()

        failed_events = list(FailedConnectionTransductorEvent.objects.all())
        critical_volt_events = list(CriticalVoltageEvent.objects.all())
        precarious_volt_events = list(PrecariousVoltageEvent.objects.all())
        phase_drop_events = list(PhaseDropEvent.objects.all())

        # assert failed events
        failed_events_interval =\
            failed_events[0].ended_at - failed_events[0].created_at
        self.assertEqual(1, len(failed_events))
        self.assertEqual(self.energy_transductor, failed_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         failed_events[0].created_at)
        self.assertEqual(datetime(2021, 3, 8, 16, 5, 4),
                         failed_events[0].ended_at)
        self.assertEqual(
            61,
            failed_events_interval.seconds
        )

        # assert critical events
        self.assertEqual(1, len(critical_volt_events))
        self.assertEqual(self.energy_transductor,
                         critical_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         critical_volt_events[0].created_at)
        self.assertEqual(None, critical_volt_events[0].ended_at)

        # assert precarious events
        precarious_1_interval =\
            precarious_volt_events[0].ended_at - \
            precarious_volt_events[0].created_at
        self.assertEqual(2, len(precarious_volt_events))
        self.assertEqual(self.energy_transductor,
                         precarious_volt_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         precarious_volt_events[0].created_at)
        self.assertEqual(datetime(2021, 3, 8, 17, 4, 3),
                         precarious_volt_events[0].ended_at)
        self.assertEqual(
            3600,
            precarious_1_interval.seconds
        )
        self.assertEqual(datetime(2021, 3, 8, 18, 4, 3),
                         precarious_volt_events[1].created_at)
        self.assertEqual(None, precarious_volt_events[1].ended_at)

        # assert phase drop events
        self.assertEqual(1, len(phase_drop_events))
        self.assertEqual(self.energy_transductor,
                         phase_drop_events[0].transductor)
        self.assertEqual(datetime(2021, 3, 8, 16, 4, 3),
                         phase_drop_events[0].created_at)
        self.assertEqual(None, phase_drop_events[0].ended_at)
