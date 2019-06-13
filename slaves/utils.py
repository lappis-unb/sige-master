from .models import Slave
from transductors.models import EnergyTransductor
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
