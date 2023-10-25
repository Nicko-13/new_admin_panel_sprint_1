import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Genre(models.Model):
    # Типичная модель в Django использует число в качестве id. В таких ситуациях поле не описывается в модели.
    # Вам же придётся явно объявить primary key.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Первым аргументом обычно идёт человекочитаемое название поля
    name = models.CharField('name', max_length=255)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField('description', blank=True)
    # auto_now_add автоматически выставит дату создания записи 
    created = models.DateTimeField(auto_now_add=True)
    # auto_now изменятся при каждом обновлении записи 
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Filmwork(models.Model):
    class FilmworkTypes(models.TextChoices):
        MOVIE = 'MV', _('Фильм')
        TV_SHOW = 'TS', _('Телепередача')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    title = models.TextField('title', blank=False)
    description = models.TextField('description', blank=True)
    rating = models.DecimalField('rating', blank=True, decimal_places=1, max_digits=3)
    type = models.CharField('type', choices=FilmworkTypes.choices, default=FilmworkTypes.MOVIE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title
