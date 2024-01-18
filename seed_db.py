class Seeder:
    """"Initial Data for the database."""

    def __init__(self):
        self.campus = []
        self.slave = []
        self.group_types = []
        self.groups = []
        self.energyTransductors = []
        self.minutelyMeasurements = []
        self.events = []

    def clear_db(self):
        if '--flush' in sys.argv:
            print('\t- Cleaning the DB first\n')
            os.system('./manage.py flush --no-input')

    def create_slave(self):
        slave_api = input(
            '\t- Please insert the IPAddress of your local slave: '
        )
        self.slave = Slave.objects.bulk_create([
            Slave(
                server_address=slave_api,
                port=8000,
                name="Local slave",
                active=True,
                broken=False,
            )
        ])
        print('\t  Successfully created', len(self.slave), 'slaves', '\n')

    def create_campus(self):
        print('\t- Creating campus')
        self.campus = Campus.objects.bulk_create([
            Campus(
                name='Darcy Ribeiro - Gleba A',
                acronym='Darcy A',
                geolocation_latitude=-15.7636,
                geolocation_longitude=-47.8694,
                zoom_ratio=16,
                contract_type='Azul',
                off_peak_demand=0.0,
                peak_demand=0.0,
            ),
            Campus(
                name='Faculdade do Gama',
                acronym='FGA',
                geolocation_latitude=-15.9894,
                geolocation_longitude=-48.0443,
                zoom_ratio=16,
                contract_type='Azul',
                off_peak_demand=0.0,
                peak_demand=0.0,
            )
        ])
        print('\t  Successfully created', len(self.campus), 'campus', '\n')
        
    def create_group_types(self):
        print('\t- Creating group types')
        self.group_types = GroupType.objects.bulk_create([
            GroupType(
                name='Prédio',
            ),
            GroupType(
                name='Gleba',
            )])
        print(
            '\t  Successfully created',
            len(self.group_types), 
            'group types', 
            '\n'
        )

    def create_group(self):
        print('\t- Creating groups')
        group_type = GroupType.objects.first()
        self.groups = Group.objects.bulk_create([
            Group(
                name='UED',
                type=group_type    
            ),
            Group(
                name='ICC',
                type=group_type
            )])
        print('\t  Successfully created', len(self.groups), 'groups', '\n')
        
    def create_energyTransductor(self):
        print('\t- Creating Transductors')
        slave = Slave.objects.first()
        campus = Campus.objects.all()
        group = Group.objects.first()
        self.energyTransductors = EnergyTransductor.objects.bulk_create([
            EnergyTransductor(
                serial_number="30000481",
                ip_address="164.41.86.42",
                slave_server=slave,
                geolocation_latitude=-15.9895,
                geolocation_longitude=-48.0456,
                campus=campus[1],
                firmware_version="1.42",
                name="UED1",
                model="MD30",
                grouping=[group],
                active=True,
                broken=False,
            ),
            EnergyTransductor(
                serial_number="30000484",
                ip_address="172.27.1.74",
                slave_server=slave,
                geolocation_latitude=-15.7729,
                geolocation_longitude=-47.8659,
                campus=campus[1],
                firmware_version="1.42",
                name="CPD1",
                model="MD30",
                grouping=[group],
                active=True,
                broken=False,
            ),
            EnergyTransductor(
                serial_number="30000486",
                ip_address="172.27.1.75",
                slave_server=slave,
                geolocation_latitude=-15.7728,
                geolocation_longitude=-47.8658,
                campus=campus[1],
                firmware_version="1.42",
                name="CPD2",
                model="MD30",
                grouping=[group],
                active=True,
                broken=False,
            ),
            EnergyTransductor(
                serial_number="30000247",
                ip_address="172.27.1.206",
                slave_server=slave,
                geolocation_latitude=-15.7632,
                geolocation_longitude=-47.873036,
                campus=campus[1],
                firmware_version="1.42",
                name="FT I",
                model="MD30",
                grouping=[group],
                active=True,
                broken=False,
            )])
        print(
            '\t  Successfully created', 
            len(self.energyTransductors), 
            'energy transductors',
            '\n'
        )
        
    def create_events(self):
        print('\t- Creating Events')
        t = EnergyTransductor.objects.all()
        self.events = []
        self.events.append([
            CriticalVoltageEvent.objects.create(
                transductor=t[0]
            ),
            CriticalVoltageEvent.objects.create(
                transductor=t[1]
            ),
            CriticalVoltageEvent.objects.create(
                transductor=t[2]
            ),
            PrecariousVoltageEvent.objects.create(
                transductor=t[0],
                data={
                    "voltage_a": random.randint(150, 200),
                    "voltage_b": random.randint(150, 200),
                    "voltage_c": random.randint(150, 200)}
            ),
            PrecariousVoltageEvent.objects.create(
                transductor=t[1],
                data={
                    "voltage_a": random.randint(150, 200),
                    "voltage_b": random.randint(150, 200),
                    "voltage_c": random.randint(150, 200)}
            ),
            PrecariousVoltageEvent.objects.create(
                transductor=t[2],
                data={
                    "voltage_a": random.randint(150, 200),
                    "voltage_b": random.randint(150, 200),
                    "voltage_c": random.randint(150, 200)}
            ),
            PhaseDropEvent.objects.create(
                transductor=t[0]
            ),
            PhaseDropEvent.objects.create(
                transductor=t[1]
            ),
            PhaseDropEvent.objects.create(
                transductor=t[2]
            )
        ])
        print('\t  Successfully created', len(self.events), 'events', '\n')
    
    def create_quartely_measurements(self):
        print('\t- Creating QuarterlyMeasurement...')
        t = EnergyTransductor.objects.all()
        now = datetime.now()
        for i in range(7 * 24 * 4):
            QuarterlyMeasurement.objects.create(
                transductor=t[i % len(self.energyTransductors)],
                collection_date=now,
                consumption_peak_time=random.random() * 1000,
                consumption_off_peak_time=random.random() * 1000
            )
            now = now - timedelta(seconds=60 * 15)
        print('\t  Successfully created 7 days of quartely measurements', '\n')
        
    def create_minutely_measurements(self):
        print('\t- Creating MinutelyMeasurement...')
        t = EnergyTransductor.objects.all()
        now = datetime.now()
        """ TODO Improve ranges """ 
        days = 1
        for i in range(days * 24 * 60):
            measurement = MinutelyMeasurement.objects.create(
                transductor=t[i % len(self.energyTransductors)],
                collection_date=now,
                frequency_a=random.randrange(221),
                voltage_a=random.randrange(221),
                voltage_b=random.randrange(221),
                voltage_c=random.randrange(221),
                current_a=random.randrange(250),
                current_b=random.randrange(240),
                current_c=random.randrange(250),
                active_power_a=random.randrange(50000),
                active_power_b=random.randrange(50000),
                active_power_c=random.randrange(50000),
                total_active_power=random.randrange(90000),
                reactive_power_a=random.randrange(6000) * -1,
                reactive_power_b=random.randrange(4000) * -1,
                reactive_power_c=random.randrange(2100),
                total_reactive_power=random.randrange(8000) * -1,
                apparent_power_a=random.randrange(27000),
                apparent_power_b=random.randrange(32000),
                apparent_power_c=random.randrange(33000),
                total_apparent_power=random.randrange(92000),
                power_factor_a=random.uniform(-0.97, -0.99),
                power_factor_b=random.uniform(-0.97, -0.99),
                power_factor_c=random.uniform(-0.97, -0.99),
                total_power_factor=random.uniform(-0.97, -0.99),
                dht_voltage_a=random.randrange(8),
                dht_voltage_b=random.randrange(7),
                dht_voltage_c=random.randrange(9),
                dht_current_a=random.randrange(4),
                dht_current_b=random.randrange(5),
                dht_current_c=random.randrange(4)
            )
            self.minutelyMeasurements.append(measurement)
            now = now - timedelta(seconds=60)
        print(
            '\t  Successfully created', 
            days, 
            'days of quartely measurements', 
            '\n'
        )
 
    def seed(self):
        self.create_slave()
        self.create_campus()
        self.create_group_types()
        self.create_group()
        self.create_energyTransductor()
        self.create_events()
        self.create_quartely_measurements()
        self.create_minutely_measurements()


if __name__ == '__main__':
    import os
    import django
    import sys

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi_master.settings')
    django.setup()
    from campi.models import Campus
    from slaves.models import Slave
    from groups.models import GroupType, Group
    from transductors.models import EnergyTransductor
    from events.models import *
    from measurements.models import *
    from datetime import datetime, timedelta
    import random

    seeder = Seeder()

    print('Starting Seed...\n') 
    seeder.clear_db()
    seeder.seed()
    print('Finished populating DB.\n')
