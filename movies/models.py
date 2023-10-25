import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField('name', max_length=255)
    description = models.TextField('description', blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmworkTypes(models.TextChoices):
        MOVIE = 'MV', _('Фильм')
        TV_SHOW = 'TS', _('Телепередача')

    title = models.TextField('title', blank=False)
    description = models.TextField('description', blank=True)
    rating = models.FloatField('rating', blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField('type', choices=FilmworkTypes.choices, default=FilmworkTypes.MOVIE)

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title
