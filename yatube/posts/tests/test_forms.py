import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True) 

        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст',
            'group': 'Группа',
            'image': uploaded,
        }

        Post.objects.create(
            author=cls.author,
            text='Первый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_post(self):
        self.assertEqual(Post.objects.all().count(), 1)

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
            content= small_gif,
            content_type='image/gif'
        )

        url = reverse('posts:create_post')
        data = {
            'text': 'Новый пост',
            'image': uploaded,
        }
        FormTests.author_client.post(url, data=data)

        self.assertEqual(Post.objects.all().count(), 2)

        new_post = Post.objects.order_by('id').last()
        self.assertEqual(new_post.text, data['text'])
        self.assertEqual(new_post.image, "posts/small.gif")

    def test_edit_post(self):
        updated_post_text = 'Изменный пост'
        post = Post.objects.all().last()
        self.assertNotEqual(post.text, updated_post_text)

        url = reverse('posts:post_edit', kwargs={
            'post_id': post.id,
        })

        FormTests.author_client.post(url, data={
            'text': updated_post_text,
        })
        post.refresh_from_db()
        self.assertEqual(post.text, updated_post_text)

    def test_new_post_group(self):
        self.assertEqual(Post.objects.all().count(), 1)
        url = reverse('posts:create_post')
        new_post_text = 'Новый пост'
        group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        data = {
            'text': new_post_text,
            'group': group.id,
        }
        FormTests.author_client.post(url, data=data)

        self.assertEqual(Post.objects.all().count(), 2)

        new_post = Post.objects.order_by('id').filter(group=group).last()
        self.assertEqual(new_post.text, new_post_text)
        self.assertEqual(new_post.group, group)

    def test_new_post_anonim(self):
        self.assertEqual(Post.objects.all().count(), 1)

        url = reverse('posts:create_post')
        new_post_text = 'Новый пост'
        data = {
            'text': new_post_text,
        }
        response = self.client.post(url, data=data)
        # здесь мы проверяем что пост не создан анонимом
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(response.status_code, 302)

        updated_post_text = 'Изменный пост'
        post = Post.objects.all().last()

        url = reverse('posts:post_edit', kwargs={
            'post_id': post.id,
        })

        self.client.post(url, data={
            'text': updated_post_text,
        })
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(response.status_code, 302)
