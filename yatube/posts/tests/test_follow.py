from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')

        cls.reader = User.objects.create_user(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.unsubscribed_user = User.objects.create_user(
            username='unsubscribed_user'
        )
        cls.unsubscribed_user_client = Client()
        cls.unsubscribed_user_client.force_login(cls.unsubscribed_user)

    def test_follow(self):
        url = reverse('posts:profile_follow', kwargs={
            'username': FollowTests.author.username,
        })
        FollowTests.reader_client.get(url)
        self.assertTrue(Follow.objects.filter(
            author=FollowTests.author, user=FollowTests.reader
        ).exists())

    def test_unfollow(self):
        url = reverse('posts:profile_unfollow', kwargs={
            'username': FollowTests.author.username,
        })
        FollowTests.reader_client.get(url)
        self.assertFalse(Follow.objects.filter(
            author=FollowTests.author, user=FollowTests.reader
        ).exists())

    def test_post_to_followers(self):
        post = Post.objects.create(
            author=FollowTests.author,
            text='Тестовый пост',
        )
        Follow.objects.create(
            author=FollowTests.author,
            user=FollowTests.reader,
        )

        url = reverse('posts:follow_index')
        response = FollowTests.reader_client.get(url)
        posts = response.context['page_obj']
        self.assertIn(post, posts)

        response = FollowTests.unsubscribed_user_client.get(url)
        posts = response.context['page_obj']
        self.assertNotIn(post, posts)
