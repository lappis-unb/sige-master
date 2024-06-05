import httpx
from django.core.management.base import BaseCommand

from apps.locations.models import State


class Command(BaseCommand):
    help = "Populate the State table with data from IBGE"

    def add_arguments(self, parser):
        url_states = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

        parser.add_argument("--url", default=url_states, help="URL to fetch the states data from IBGE API")

    def handle(self, url, *args, **options):
        if State.objects.exists():
            self.stdout.write(self.style.WARNING("States table already populated"))
            return

        try:
            response = httpx.get(url)
            response.raise_for_status()
        except httpx.RequestError as e:
            self.stdout.write(self.style.ERROR(f"Error connecting to IBGE API: {str(e)}"))
            return
        except httpx.HTTPStatusError as e:
            self.stdout.write(self.style.ERROR(f"Unexpected response from IBGE API: {str(e)}"))
            return

        data = response.json()
        for state in data:
            State.objects.create(
                code=state["id"],
                name=state["nome"],
                acronym=state["sigla"],
                # timezone=state['regiao']['id']
            )
        self.stdout.write(self.style.SUCCESS("States populated successfully"))
