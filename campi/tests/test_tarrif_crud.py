from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Tariff, Campus


class CampiTestCase(APITestCase):

    def setUp(self):
        self.campus = Campus.objects.create(
            name="Campus da Faculdade Gama",
            acronym="FGA",
        )
        self.url_list = reverse(
            'campi:tariffs-list',
            kwargs={'campi_pk': self.campus.pk}
        )

    def tearDown(self):
        Tariff.objects.all().delete()

    def _create_campi_tarif(self):
        return Tariff.objects.create(
            campus=self.campus,
            start_date='2020-03-02',
            regular_tariff=2.50,
            high_tariff=3.50
        )

    def test_create_campi_tariff(self):

        tariff_data = {
            'start_date': '2020-03-02',
            'campus': 'http://testserver/campi/%s/' % (self.campus.pk),
            'regular_tariff': 2.50,
            'high_tariff': 3.50
        }

        response = self.client.post(
            path=self.url_list,
            data=tariff_data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            201,
            msg='Failed to create a tariff'
        )

        self.assertDictContainsSubset(
            tariff_data,
            response.data,
        )

        self.assertEqual(Tariff.objects.all().count(), 1)

    def test_patch_update_campi_tariff(self):
        self._create_campi_tarif()

        tariff_data = {
            'regular_tariff': 4.50,
            'high_tariff': 5.50
        }

        url_detail = reverse(
            'campi:tariffs-detail',
            kwargs={
                'campi_pk': self.campus.pk,
                'pk': str(Tariff.objects.last().id)
            }
        )

        response = self.client.patch(
            path=url_detail,
            data=tariff_data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            200,
            msg='Failed to patch update a tariff'
        )

        self.assertEqual(
            response.data['regular_tariff'],
            tariff_data['regular_tariff'],
        )

        self.assertEqual(
            response.data['high_tariff'],
            tariff_data['high_tariff'],
        )

    def test_list_all_campi_tariff(self):
        Tariff.objects.bulk_create([
            Tariff(campus=self.campus, start_date='2020-03-02',
                   regular_tariff=2.50, high_tariff=3.50),
            Tariff(campus=self.campus, start_date='2021-03-02',
                   regular_tariff=3.50, high_tariff=4.50),
            Tariff(campus=self.campus, start_date='2022-03-02',
                   regular_tariff=4.50, high_tariff=5.50),
        ])

        response = self.client.get(
            path=self.url_list,
            format='json',
        )

        self.assertEqual(len(response.data), 3,
                         msg='The number of tariffs returned ' \
                              'is different than 3')

    def test_delete_campi_tarrif(self):
        tariff = self._create_campi_tarif()

        url_detail = reverse(
            'campi:tariffs-detail',
            kwargs={
                'campi_pk': self.campus.pk,
                'pk': str(tariff.id)
            }
        )

        response = self.client.delete(
            path=url_detail,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            204,
            msg='Failed to delete the tariff'
        )
