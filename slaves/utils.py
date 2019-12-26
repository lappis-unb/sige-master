import os
import json
import urllib.request
from datetime import datetime
from datetime import timedelta

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


class CheckTransductorsAndSlaves():

    def check_transductors(self):

        slaves = Slave.objects.all()

        for slave in slaves:
            slave.broken = False
            slave.save()

            # to work in dev dont forget to insert the port
            url = 'http://' + slave.ip_address + ":" + \
                os.getenv('SLAVE_PORT') + '/broken_transductors'
            try:
                web_request = urllib.request.urlopen(url)

                if(web_request.status == 200):
                    data = web_request.read()

                    encoding = web_request.info().get_content_charset('utf-8')

                    transductors = json.loads(data.decode(encoding))

                    for transductor in transductors:
                        transductor_status = EnergyTransductor.objects.get(
                            serial_number=transductor['serial_number'])
                        transductor_status.broken = transductor['broken']
                        transductor_status.save()

                else:
                    slave.broken = True
                    FailedConnectionSlaveEvent.save_event(slave)
                    slave.save()

            except Exception:
                slave.broken = True
                FailedConnectionSlaveEvent.save_event(slave)
                slave.save()


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
            active_max_power_list_off_peak_time=(
                msm['active_max_power_list_off_peak_time']
            ),
            reactive_max_power_list_peak_time=(
                msm['reactive_max_power_list_peak_time']
            ),
            reactive_max_power_list_off_peak_time=(
                msm['reactive_max_power_list_off_peak_time']
            ),
            collection_time=msm['collection_date'],
            transductor_id=transductor.serial_number
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
            collection_time=msm['collection_date'],
            transductor_id=transductor.serial_number
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
            collection_time=msm['collection_date'],
            transductor_id=transductor.serial_number
        )

    @staticmethod
    def save_event_object(event_class, event_dict):
        """
        Builds and saves events from a dict to a given class
        """
        if event_class.__name__ == 'FailedConnectionTransductorEvent':
            FailedConnectionTransductorEvent.objects.create(
                created_at=event_dict.created_at,
                transductor=EnergyTransductor.objects.find(
                    ip_address=event_dict.ip_address
                )
            )
        else:
            event_class.objects.create(**event_dict)    # creates from dict

    @staticmethod
    def get_events():
        """
        Collects all events previously created on the slave slave servers
        """
        slave_servers = Slave.objects.all()

        for slave in slave_servers:
            event_responses = request_all_events(slave)

            for pairs in event_responses:
                event_class = globals()[pairs[0]]    # gets class from string
                event = json.loads(pairs[1].content)
                DataCollector.save_event_object(event_class, event)

    @staticmethod
    def get_measurements(*args, **kwargs):
        """
        Collects a given set of measurements from all slave servers
        """
        slaves = Slave.objects.all()

        for slave in slaves:
            for transductor in slave.transductors.all():
                if kwargs.get('minutely', None):
                    # Get response and save it in the master database
                    minutely_response = request_measurements(
                        slave,
                        transductor,
                        transductor.last_data_collection,
                        "minutely"
                    )

                    measurements = json.loads(minutely_response.content)

                    for msm in measurements['results']:
                        # Create MinutelyMeasurement object
                        try:
                            DataCollector.build_minutely_measurements(
                                msm, transductor
                            )
                            transductor.last_data_collection = datetime.now()
                        except Exception as exception:
                            print(exception)
                            pass

                if kwargs.get('quarterly', None):
                    quarterly_response = request_measurements(
                        slave,
                        transductor,
                        transductor.last_data_collection,
                        "quarterly"
                    )

                    measurements = json.loads(quarterly_response.content)

                    for msm in measurements['results']:
                        # Create QuarterlyMeasurement object
                        try:
                            DataCollector.build_quarterly_measurements(
                                msm, transductor
                            )
                            transductor.last_data_collection = datetime.now()
                        except Exception:
                            pass

                if kwargs.get('monthly', None):
                    monthly_response = request_measurements(
                        slave,
                        transductor,
                        transductor.last_data_collection,
                        "monthly"
                    )

                    measurements = json.loads(monthly_response.content)

                    for msm in measurements['results']:
                        # Create MonthlyMeasurement object
                        try:
                            DataCollector.build_monthly_measurements(
                                msm, transductor
                            )
                            transductor.last_data_collection = datetime.now()
                        except Exception:
                            pass
