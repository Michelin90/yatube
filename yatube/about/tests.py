from http import HTTPStatus

from django.test import Client, TestCase


class AboutUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_is_exists_at_desierd_location(self):
        """Страницы author, tech доступны любому пользователю."""
        status_of_pages = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for url, status in status_of_pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_templates(self):
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
