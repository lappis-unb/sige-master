import os
import json
import urllib.request
from datetime import timedelta
from django.utils.timezone import datetime

from .models import Slave
from .api import request_all_events
from .api import request_measurements

from events.models import PhaseDropEvent
from events.models import CriticalVoltageEvent
from events.models import PrecariousVoltageEvent
from events.models import FailedConnectionSlaveEvent
from events.models import FailedConnectionTransductorEvent

from transductors.models import EnergyTransductor

from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement
from measurements.models import MonthlyMeasurement
from measurements.models import RealTimeMeasurement


class CheckTransductorsAndSlaves():

    def check_transductors(self):

        slaves = Slave.objects.all()

        for slave in slaves:
            # to work in dev dont forget to insert the port
            url = 'http://' + slave.ip_address + ":" + \
                os.getenv('SLAVE_PORT') + '/broken-transductors'
            try:
                web_request = urllib.request.urlopen(url)

                if(web_request.status == 200):
                    data = web_request.read()

                    encoding = web_request.info().get_content_charset('utf-8')

                    transductors = json.loads(data.decode(encoding))

                    for transductor in transductors:
                        transductor_status = EnergyTransductor.objects.get(
                            id=transductor['id'])
                        transductor_status.broken = transductor['broken']
                        transductor_status.save()

                    slave.set_broken(False)
                else:
                    slave.set_broken(True)

            except Exception:
                slave.set_broken(True)

# TODO Não sabemos como resolver essa comunicação
# Transdutores em mais de um slave tem que ser tratados de forma diferente?


class DataCollector():
    @staticmethod
    def build_monthly_measurements(msm, transductor):
        MonthlyMeasurement.objects.create(
            generated_energy_peak_time=msm['generated_energy_peak_time'],
            generated_energy_off_peak_time=(
                msm['generated_energy_off_peak_time']
            ),
            consumption_peak_time=msm['consumption_peak_time'],
            consumption_off_peak_time=msm['consumption_off_peak_time'],
            inductive_power_peak_time=msm['inductive_power_peak_time'],
            inductive_power_off_peak_time=msm['inductive_power_off_peak_time'],
            capacitive_power_peak_time=msm['capacitive_power_peak_time'],
            capacitive_power_off_peak_time=(
                msm['capacitive_power_off_peak_time']
            ),
            active_max_power_peak_time=msm['active_max_power_peak_time'],
            active_max_power_off_peak_time=(
                msm['active_max_power_off_peak_time']
            ),
            reactive_max_power_peak_time=msm['reactive_max_power_peak_time'],
            reactive_max_power_off_peak_time=(
                msm['reactive_max_power_off_peak_time']
            ),
            active_max_power_list_peak_time=(
                msm['active_max_power_list_peak_time']
            ),
            active_max_power_list_peak=(
                msm['active_max_power_list_peak']
            ),
            active_max_power_list_off_peak_time=(
                msm['active_max_power_list_off_peak_time']
            ),
            active_max_power_list_off_peak=(
                msm['active_max_power_list_off_peak']
            ),
            reactive_max_power_list_peak_time=(
                msm['reactive_max_power_list_peak_time']
            ),
            reactive_max_power_list_peak=(
                msm['reactive_max_power_list_peak']
            ),
            reactive_max_power_list_off_peak_time=(
                msm['reactive_max_power_list_off_peak_time']
            ),
            reactive_max_power_list_off_peak=(
                msm['reactive_max_power_list_off_peak']
            ),
            collection_date=msm['transductor_collection_date'],
            transductor_id=transductor.id
        )

    @staticmethod
    def build_minutely_measurements(msm, transductor):
        MinutelyMeasurement.objects.create(
            frequency_a=msm['frequency_a'],
            voltage_a=msm['voltage_a'],
            voltage_b=msm['voltage_b'],
            voltage_c=msm['voltage_c'],
            current_b=msm['current_a'],
            current_a=msm['current_b'],
            current_c=msm['current_c'],
            active_power_a=msm['active_power_a'],
            active_power_b=msm['active_power_b'],
            active_power_c=msm['active_power_c'],
            total_active_power=msm['total_active_power'],
            reactive_power_a=msm['reactive_power_a'],
            reactive_power_b=msm['reactive_power_b'],
            reactive_power_c=msm['reactive_power_c'],
            total_reactive_power=msm['total_reactive_power'],
            apparent_power_a=msm['apparent_power_a'],
            apparent_power_b=msm['apparent_power_b'],
            apparent_power_c=msm['apparent_power_c'],
            total_apparent_power=msm['total_apparent_power'],
            power_factor_a=msm['power_factor_a'],
            power_factor_b=msm['power_factor_b'],
            power_factor_c=msm['power_factor_c'],
            total_power_factor=msm['total_power_factor'],
            dht_voltage_a=msm['dht_voltage_a'],
            dht_voltage_b=msm['dht_voltage_b'],
            dht_voltage_c=msm['dht_voltage_c'],
            dht_current_a=msm['dht_current_a'],
            dht_current_b=msm['dht_current_b'],
            dht_current_c=msm['dht_current_c'],
            collection_date=msm['transductor_collection_date'],
            transductor_id=transductor.id
        )

    @staticmethod
    def build_quarterly_measurements(msm, transductor):
        QuarterlyMeasurement.objects.create(
            generated_energy_peak_time=msm['generated_energy_peak_time'],
            generated_energy_off_peak_time=(
                msm['generated_energy_off_peak_time']
            ),
            consumption_peak_time=msm['consumption_peak_time'],
            consumption_off_peak_time=msm['consumption_off_peak_time'],
            inductive_power_peak_time=msm['inductive_power_peak_time'],
            inductive_power_off_peak_time=(
                msm['inductive_power_off_peak_time']
            ),
            capacitive_power_peak_time=msm['capacitive_power_peak_time'],
            capacitive_power_off_peak_time=(
                msm['capacitive_power_off_peak_time']
            ),
            collection_date=msm['transductor_collection_date'],
            transductor_id=transductor.id
        )

    @staticmethod
    def save_event_object(event_dict, request_type):
        """
        Builds and saves events from a dict to a given class
        """
        DataCollector.build_events(event_dict)

    @staticmethod
    def build_events(events):
        for event_dict in events:
            event_class = globals()[event_dict['type']]
            transductor = EnergyTransductor.objects.get(
                ip_address=event_dict['ip_address']
            )
            last_event = event_class.objects.filter(
                transductor=transductor,
                ended_at__isnull=True
            ).last()
            if last_event:
                if not event_dict['ended_at']:
                    last_event.data = event_dict['data']
                    last_event.save()
                else:
                    last_event.data = event_dict['data']
                    last_event.ended_at = event_dict['ended_at']
                    last_event.save()
            else:
                if not event_dict['ended_at']:
                    event_class().save_event(transductor, event_dict)

    @staticmethod
    def get_events():
        """
        Collects all events previously created on the slave servers
        """
        slave_servers = Slave.objects.all()

        for slave in slave_servers:
            event_responses = request_all_events(slave)
            for pairs in event_responses:
                loaded_events = json.loads(pairs[1].content)
                DataCollector.save_event_object(loaded_events, pairs[0])

    @staticmethod
    def build_realtime_measurements(msm, transductor):
        if RealTimeMeasurement.objects.filter(transductor=transductor):
            measurement = RealTimeMeasurement.objects.get(
                transductor=transductor
            )
            measurement.voltage_a = msm['voltage_a']
            measurement.voltage_b = msm['voltage_b']
            measurement.voltage_c = msm['voltage_c']
            measurement.current_a = msm['current_a']
            measurement.current_b = msm['current_b']
            measurement.current_c = msm['current_c']
            measurement.total_active_power = msm['total_active_power']
            measurement.total_reactive_power = msm['total_reactive_power']
            measurement.total_power_factor = msm['total_power_factor']
            measurement.transductor = transductor
            measurement.collection_date = datetime.strptime(
                msm['transductor_collection_date'], 
                '%Y-%m-%dT%H:%M:%S.%f'
            )

            measurement.save()
        else:
            RealTimeMeasurement.objects.create(
                voltage_a=msm['voltage_a'],
                voltage_b=msm['voltage_b'],
                voltage_c=msm['voltage_c'],
                current_a=msm['current_a'],
                current_b=msm['current_b'],
                current_c=msm['current_c'],
                total_active_power=msm['total_active_power'],
                total_reactive_power=msm['total_reactive_power'],
                total_power_factor=msm['total_power_factor'],
                transductor=transductor,
                collection_date=datetime.strptime(
                    msm['transductor_collection_date'],
                    '%Y-%m-%dT%H:%M:%S.%f'
                )
            )

    @staticmethod
    def get_measurements(*args, **kwargs):
        """
        Collects a given set of measurements from all slave servers
        """
        slaves = Slave.objects.all()

        collection_date = datetime.now()
        for slave in slaves:
            if kwargs.get('realtime', None):
                realtime_response = request_measurements(
                    'realtime-measurements',
                    slave
                )

                measurement = json.loads(realtime_response.content)
                for transductor_data in measurement:
                    try:
                        transductor = EnergyTransductor.objects.get(
                            id=transductor_data['transductor_id']
                        )
                        DataCollector.build_realtime_measurements(
                            transductor_data, transductor
                        )
                    except Exception as exception:
                        print(exception)

            for transductor in slave.transductors.all():
                collection_date = datetime.now()
                if kwargs.get('minutely', None):
                    # Get response and save it in the master database
                    minutely_response = request_measurements(
                        "minutely-measurements",
                        slave,
                        transductor,
                        transductor.last_minutely_collection,
                        collection_date
                    )

                    measurements = json.loads(minutely_response.content)

                    for msm in measurements:
                        # Create MinutelyMeasurement object
                        try:
                            DataCollector.build_minutely_measurements(
                                msm, transductor
                            )
                        except Exception as exception:
                            pass
                    transductor.last_minutely_collection = collection_date
                    transductor.save()

                if kwargs.get('quarterly', None):
                    quarterly_response = request_measurements(
                        "quarterly-measurements",
                        slave,
                        transductor,
                        transductor.last_quarterly_collection,
                        collection_date
                    )

                    measurements = json.loads(quarterly_response.content)

                    for msm in measurements:
                        # Create QuarterlyMeasurement object
                        # try:
                        DataCollector.build_quarterly_measurements(
                            msm, transductor
                        )
                        # except Exception:
                        # pass

                    transductor.last_quarterly_collection = collection_date
                    transductor.save()

                if kwargs.get('monthly', None):
                    monthly_response = request_measurements(
                        "monthly-measurements",
                        slave,
                        transductor,
                        transductor.last_monthly_collection,
                        collection_date
                    )

                    measurements = json.loads(monthly_response.content)

                    for msm in measurements:
                        # Create MonthlyMeasurement object
                        # try:
                        DataCollector.build_monthly_measurements(
                            msm, transductor
                        )
                        # except Exception:
                        #     pass

                    transductor.last_monthly_collection = collection_date
                    transductor.save()
