from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint 

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default='')
    description = models.TextField(default='', max_length=30)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='можете загрузить картинку'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        'date published',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Пост комментария'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    follow_time = models.DateTimeField(auto_now=True)

    class Meta:
        UniqueConstraint(fields=['author', 'user'], name='unique_follow')
