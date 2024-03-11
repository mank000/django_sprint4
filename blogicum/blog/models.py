from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import BaseModel

User = get_user_model()


class Category(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=256,
        blank=False
    )
    description = models.TextField('Описание', blank=False)
    slug = models.SlugField(
        'Идентификатор',
        blank=False,
        unique=True,
        help_text=('Идентификатор страницы для URL; разрешены символы'
                   'латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField('Название места', max_length=256, blank=False)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
        blank=False
    )
    text = models.TextField('Текст', blank=False)
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        blank=False,
        help_text=('Если установить дату и время в будущем '
                   '— можно делать отложенные публикации.')
    )
    image = models.ImageField(
        'Фото',
        upload_to='birthdays_images',
        blank=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        blank=False
    )

    def get_absolute_url(self):
        return reverse('blog:profile', kwargs={'username': self.author})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.title


class Comment(BaseModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
