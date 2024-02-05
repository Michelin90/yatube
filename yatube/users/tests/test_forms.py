from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_new_user_in_db(self):
        user_count = User.objects.count()
        form_data = {
            'password1': 'new_password',
            'password2': 'new_password',
            'username': 'new_user',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='new_user'
            ).exists()
        )
