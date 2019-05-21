import pytest
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from users.models import CustomUser


class UsersTestCase(TestCase):

    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            email='admin@admin.com',
            name='admin',
            username='admin',
            user_type='adm',
            password='password'
        )

        self.researcher_user = CustomUser.objects.create_superuser(
            email='researcher@researcher.com',
            name='researcher',
            username='researcher',
            user_type='rsc',
            password='password'
        )

        self.manager_user = CustomUser.objects.create_superuser(
            email='manager@manager.com',
            name='manager',
            username='manager',
            user_type='man',
            password='password'
        )

    def test_create_new_researcher(self):
        user = CustomUser.objects.create_superuser(
            email='email@email.com',
            name='usuário',
            username='user',
            user_type='rsc',
            password='password'
        )

        new_user = CustomUser.objects.last()

        self.assertEqual(new_user.user_type, 'rsc')

    def test_create_new_manager(self):
        user = CustomUser.objects.create_superuser(
            email='email@email.com',
            name='usuário',
            username='user',
            user_type='man',
            password='password'
        )

        new_user = CustomUser.objects.last()

        self.assertEqual(new_user.user_type, 'man')

    def test_create_new_admin(self):
        user = CustomUser.objects.create_superuser(
            email='email@email.com',
            name='usuário',
            username='user',
            user_type='adm',
            password='password'
        )

        new_user = CustomUser.objects.last()

        self.assertEqual(new_user.user_type, 'adm')

    def test_read_user_by_email(self):
        user = CustomUser.objects.get(email='admin@admin.com')

        self.assertIsNotNone(user)

    def test_read_user_by_name(self):
        user = CustomUser.objects.get(name='admin')

        self.assertIsNotNone(user)

    def test_read_user_by_username(self):
        user = CustomUser.objects.get(username='admin')

        self.assertIsNotNone(user)

    def test_read_user_by_user_type(self):
        admin_user = CustomUser.objects.get(user_type='adm')
        researcher_user = CustomUser.objects.get(user_type='rsc')
        manager_user = CustomUser.objects.get(user_type='man')

        self.assertIsNotNone(admin_user)
        self.assertIsNotNone(researcher_user)
        self.assertIsNotNone(manager_user)

    def test_not_read_user_password(self):
        user = CustomUser.objects.get(email='admin@admin.com')

        self.assertNotEqual(user.password, 'password')

    def test_update_new_name(self):
        user = CustomUser.objects.get(email='admin@admin.com')
        user.name = 'new admin'
        user.save()

        self.assertEqual(user.name, 'new admin')

    def test_update_new_email(self):
        user = CustomUser.objects.get(email='admin@admin.com')
        user.email = 'new_admin@admin.com'
        user.save()

        self.assertEqual(user.email, 'new_admin@admin.com')

    def test_update_new_username(self):
        user = CustomUser.objects.get(email='admin@admin.com')
        user.username = 'new_admin'
        user.save()

        self.assertEqual(user.username, 'new_admin')

    def test_update_another_user_type(self):
        user = CustomUser.objects.get(email='admin@admin.com')
        user.user_type = 'rsc'
        user.save()

        self.assertEqual(user.user_type, 'rsc')

    def test_not_update_user_with_equal_email(self):
        user = CustomUser.objects.get(email='researcher@researcher.com')
        user.email = 'admin@admin.com'

        with self.assertRaises(ValidationError):
            user.save()

    def test_not_update_user_with_equal_username(self):
        user = CustomUser.objects.get(username='researcher')
        user.username = 'admin'

        with self.assertRaises(ValidationError):
            user.save()

    def test_delete_existent_user_of_all_types(self):
        admin_user = CustomUser.objects.get(
            email='admin@admin.com'
        )
        researcher_user = CustomUser.objects.get(
            email='researcher@researcher.com'
        )
        manager_user = CustomUser.objects.get(
            email='manager@manager.com'
        )

        with self.assertRaises(CustomUser.DoesNotExist):
            admin_user.delete()
            CustomUser.objects.get(
                email='admin@admin.com'
            )

        with self.assertRaises(CustomUser.DoesNotExist):
            researcher_user.delete()
            CustomUser.objects.get(
                email='researcher@researcher.com'
            )

        with self.assertRaises(CustomUser.DoesNotExist):
            manager_user.delete()
            CustomUser.objects.get(
                email='manager@manager.com'
            )

    def test_try_delete_inexistent_user(self):
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(email='admin@researcher.com')
