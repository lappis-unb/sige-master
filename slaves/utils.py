from .api import *
from .models import Slave
from transductors.models import EnergyTransductor
from datetime import datetime, timedelta
import urllib.request
import json
import os


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
                    slave.save()

            except Exception:
                slave.broken = True
                slave.save()


# TODO Não sabemos como resolver essa comunicação
# Transdutores em mais de um slave tem que ser tratados de forma diferente?

class DataCollector():
    @staticmethod
    def get_measurements(*args, **kwargs):
        slaves = Slave.objects.all()
        start_date = datetime.strftime(datetime.now() - timedelta(1),
                                       '%Y-%m-%d')

        for slave in slaves:
            print(slave.transductors.all())
            for transductor in slave.transductors.all():
                if kwargs.get('minutely', None):
                    # Get response and save it in the master database
                    request_measurements(slave,
                                         transductor,
                                         start_date,
                                         "minutely")
                if kwargs.get('quarterly', None):
                    request_measurements(slave,
                                         transductor,
                                         start_date,
                                         "quarterly")
                if kwargs.get('monthly', None):
                    request_measurements(slave,
                                         transductor,
                                         start_date,
                                         "monthly")
