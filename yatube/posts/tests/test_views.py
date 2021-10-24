import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    def setUp(self):
        cache.clear()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        user = User.objects.create_user(username='user')

        cls.reader = User.objects.create_user(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.posts = []
        for idx in range(10):
            post = Post.objects.create(
                author=user,
                text=f'Тестовый пост {idx}',
                image=uploaded
            )
            cls.posts.append(post)

        cls.group_posts = []
        for idx in range(15):
            post = Post.objects.create(
                author=user,
                text=f'Тестовый пост {idx} в группе "{cls.group.title}"',
                group=cls.group,
                image=uploaded
            )
            cls.group_posts.append(post)

        cls.user_posts = []
        for idx in range(12):
            post = Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {idx}"',
                image=uploaded
            )
            cls.user_posts.append(post)

        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='OtherSlug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': ViewTests.group.slug
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': ViewTests.reader.username
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': ViewTests.posts[0].id
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': ViewTests.user_posts[0].id
            }): 'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = ViewTests.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        expected_order = sorted(Post.objects.all(),
                                key=lambda x: x.pub_date, reverse=True)
        expected_contexts = {
            reverse('posts:index'): expected_order[:10],
            reverse('posts:index') + "?page=2": expected_order[10:20],
            reverse('posts:index') + "?page=3": expected_order[20:30],
            reverse('posts:index') + "?page=4": expected_order[30:],
        }

        for reverse_name, expected_posts in expected_contexts.items():
            with self.subTest(reverse_name):
                response = ViewTests.author_client.get(reverse_name)
                self.assertSequenceEqual(list(response.context['page_obj']),
                                         expected_posts)
                for post in response.context['page_obj']:
                    self.assertTrue(post.image.url.startswith(
                        "/media/posts/"
                    ))

    def test_group_context(self):
        expected_order = sorted(ViewTests.group_posts,
                                key=lambda x: x.pub_date, reverse=True)
        expected_contexts = {
            reverse('posts:group_list', kwargs={
                'slug': ViewTests.group.slug
            }): expected_order[:10],
            reverse('posts:group_list', kwargs={
                'slug': ViewTests.group.slug
            }) + "?page=2": expected_order[10:],
        }

        for reverse_name, expected_posts in expected_contexts.items():
            with self.subTest(reverse_name):
                response = ViewTests.author_client.get(reverse_name)
                self.assertSequenceEqual(list(response.context['page_obj']),
                                         expected_posts)
                for post in response.context['page_obj']:
                    self.assertTrue(
                        post.image.url.startswith("/media/posts/")
                    )

    def test_profile_context(self):
        expected_order = sorted(ViewTests.user_posts,
                                key=lambda x: x.pub_date, reverse=True)
        expected_contexts = {
            reverse('posts:profile', kwargs={
                'username': ViewTests.author.username
            }): expected_order[:10],
            reverse('posts:profile', kwargs={
                'username': ViewTests.author.username
            }) + "?page=2": expected_order[10:],
        }

        for reverse_name, expected_posts in expected_contexts.items():
            with self.subTest(reverse_name):
                response = ViewTests.author_client.get(reverse_name)
                self.assertSequenceEqual(list(response.context['page_obj']),
                                         expected_posts)
                for post in response.context['page_obj']:
                    self.assertTrue(post.image.url.startswith("/media/posts/"))

    def test_post_context(self):
        url = reverse('posts:post_detail', kwargs={
            'post_id': ViewTests.posts[5].id
        })
        response = ViewTests.author_client.get(url)
        assert response.context['post'] == ViewTests.posts[5]
        self.assertTrue(
            response.context['post'].image.url.startswith("/media/posts/small")
        )

    def test_post_edit_context(self):
        url = reverse('posts:post_edit', kwargs={
            'post_id': ViewTests.user_posts[0].id
        })
        response = ViewTests.author_client.get(url)
        assert response.context['form'].instance == ViewTests.user_posts[0]

    def test_post_create_context(self):
        url = reverse('posts:create_post')
        response = ViewTests.author_client.get(url)
        assert isinstance(response.context['form'].instance, Post)

    def test_post_creation_in_group(self):
        url = reverse('posts:create_post')
        data = {
            'text': 'Новый пост',
            'group': ViewTests.group.id,
        }
        ViewTests.author_client.post(url, data=data)

        new_post = Post.objects.all().first()
        urls_to_check = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={
                'username': ViewTests.author.username
            }),
            reverse('posts:group_list', kwargs={
                'slug': ViewTests.group.slug
            }),
        ]

        for url in urls_to_check:
            response = ViewTests.author_client.get(url)
            first_post = response.context['page_obj'][0]
            assert first_post == new_post

        another_group_url = reverse('posts:group_list', kwargs={
            'slug': ViewTests.another_group.slug,
        })
        response = ViewTests.author_client.get(another_group_url)
        assert len(response.context['page_obj']) == 0

    def test_comment(self):
        post = Post.objects.create(
            author=ViewTests.author, text='Тестовый пост'
        )
        form_data = {
            'text': 'текст'
        }
        response = self.author_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'], post_id=post.id, author=self.author
        ))
