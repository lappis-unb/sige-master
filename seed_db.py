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
        slave_api = input('\t- Please insert the IPAddress of your local slave: ')
        self.slave = Slave.objects.bulk_create([
            Slave(
                ip_address=slave_api,
                port=8000,
                name="Local slave"
            )
        ])

    def create_campus(self):
        print('\t- Creating campus')
        self.campus = Campus.objects.bulk_create([
            Campus(
                name='Darcy Ribeiro - Gleba A',
                acronym='Darcy A',
                geolocation_latitude=-15.7636,
                geolocation_longitude=-47.8694,
            ),
            Campus(
                name='Faculdade do Gama',
                acronym='FGA',
                geolocation_latitude=-15.9894,
                geolocation_longitude=-48.0443,
            ),
            
        ])
    
    def create_group_types(self):
        print('\t- Creating group types')
        self.group_types = GroupType.objects.bulk_create([
            GroupType(
                name='Prédio',
            ),
            GroupType(
                name='Gleba',
            ),
            
        ])

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
            ),
            
        ])

    def create_energyTransductor(self):
        print('\t- Creating Transductors')
        slave = Slave.objects.first()
        campus= Campus.objects.all()
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
            ),
        ])

    def create_events(self):
        print('\t- Creating Events')
        t = EnergyTransductor.objects.all()
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
                transductor=t[0]
        ),
        PrecariousVoltageEvent.objects.create(
                transductor=t[1]
        ),
        PrecariousVoltageEvent.objects.create(
                transductor=t[2]
        ),
        PhaseDropEvent.objects.create(
                transductor=t[0]
        ),
        PhaseDropEvent.objects.create(
                transductor=t[1]
        ),
        PhaseDropEvent.objects.create(
                transductor=t[2]
        )])


    def seed(self):
        self.create_slave()
        self.create_campus()
        self.create_group_types()
        self.create_group()
        self.create_energyTransductor()
        self.create_events()



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
    from datetime import datetime

    seeder = Seeder()

    print('Starting Seed...\n') 
    seeder.clear_db()
    seeder.seed()
    print('Finished populating DB.\n')