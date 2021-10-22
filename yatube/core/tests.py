from django.test import TestCase
from django.urls import reverse

class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
        # Проверьте, что статус ответа сервера - 404
        # Проверьте, что используется шаблон core/404.html
