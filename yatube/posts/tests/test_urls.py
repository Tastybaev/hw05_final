from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        cache.clear()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create_user(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая группа',
        )

    def test_static_pages(self):
        url_pages = [
            '/',
            '/about/author/',
            '/about/tech/',
        ]
        for url in url_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_return_correct_codes(self):
        # url -> (anonymous, reader, author)
        code_url_names = {
            '/': (200, 200, 200),
            f'/group/{StaticURLTests.group.slug}/': (200, 200, 200),
            f'/profile/{StaticURLTests.author.username}/': (200, 200, 200),
            f'/posts/{StaticURLTests.post.id}/': (200, 200, 200),
            f'/posts/{StaticURLTests.post.id}/edit/': (302, 200, 200),
            '/create': (301, 200, 200),
            '/unexisting_page': (404, 404, 404),
        }
        for url, codes in code_url_names.items():
            anon_code, reader_code, author_code = codes
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, anon_code)
                response = self.reader_client.get(url, follow=True)
                self.assertEqual(response.status_code, reader_code)
                response = self.author_client.get(url, follow=True)
                self.assertEqual(response.status_code, author_code)

    def test_urls_uses_correct_template_anonymous(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{StaticURLTests.author.username}/':
            'posts/profile.html',
            f'/posts/{StaticURLTests.post.id}/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_reader(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{StaticURLTests.author.username}/':
            'posts/profile.html',
            f'/posts/{StaticURLTests.post.id}/': 'posts/post_detail.html',
            '/create': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.reader_client.get(url, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_author(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{StaticURLTests.author.username}/':
            'posts/profile.html',
            f'/posts/{StaticURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{StaticURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertTemplateUsed(response, template)

    def test_cache(self):
        posts_count = Post.objects.count()
        response = self.client.get('/').content
        Post.objects.create(
            author=self.author,
            text='Тестовая группа',)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response, self.client.get('/').content)
        cache.clear()
        self.assertNotEqual(
            response, self.client.get('/').content)
