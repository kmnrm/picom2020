from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from django.contrib.auth.models import User, Group


class UserAuthTests(APITestCase):
    def setUp(self):
        Group.objects.get_or_create(name='users')

        self.user_data = {
            'username': 'Vladimir',
            'password': 'Pooteen'
        }
        self.users_count = User.objects.all().count()

    def test_create_action(self):
        url = reverse('users-list')
        response = self.client.post(url, self.user_data, format='json')
        user = User.objects.all().last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.users_count + 1, User.objects.all().count())
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(
            user.groups.all().first().name,
            Group.objects.all().first().name
        )

    def test_api_auth_post_action(self):
        client = APIClient()
        url = reverse('users-list')
        self.client.post(url, self.user_data, format='json')
        response = client.post(
            '/api/token/',
            {
                'username': self.user_data['username'],
                'password':  self.user_data['password']
            },
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('access', response.data.keys())
        self.assertIn('refresh', response.data.keys())
