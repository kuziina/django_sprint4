"""Модели приложения blog."""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    """Абстрактная модель."""

    is_published = models.BooleanField(
        default=True,
        blank=False,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name='Добавлено'
    )

    class Meta:
        """Метаданные модели BaseModel."""

        abstract = True


class Post(BaseModel):
    """Модель публикации."""

    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images/',
        blank=True,
    )

    class Meta:
        """Метаданные модели Post."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


class Category(BaseModel):
    """Модель категории публикаций."""

    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    def __str__(self):
        return self.title

    class Meta:
        """Метаданные модели Category."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    """Модель места публикации."""

    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места')

    def __str__(self):
        return self.name

    class Meta:
        """Метаданные модели Location."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Comment(BaseModel):
    """Модель комментария к публикации."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    class Meta:
        """Метаданные модели Comment."""

        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
