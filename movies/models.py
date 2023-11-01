import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, unique=True)

    class Meta:
        db_table = 'content\'.\'genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full name'), blank=False)

    class Meta:
        db_table = 'content\'.\'person'
        verbose_name = _('film crew member')
        verbose_name_plural = _('film crew')

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        try:
            Person.objects.get(full_name=self.full_name)
        except Person.DoesNotExist:
            super().save(*args, **kwargs)


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmworkTypes(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv_show')

    title = models.TextField(_('title'), blank=False)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation date'), blank=True)
    rating = models.FloatField(
        _('rating'),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(
        _('type'),
        choices=FilmworkTypes.choices,
        default=FilmworkTypes.MOVIE,
    )

    # Many-to-many fields declarations
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = 'content\'.\'film_work'
        verbose_name = _('film work')
        verbose_name_plural = _('film works')

        indexes = [models.Index(fields=['creation_date'], name='film_work_creation_date_idx')]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    class Meta:
        db_table = 'content\'.\'genre_film_work'
        verbose_name = _('film\'s genre')
        verbose_name_plural = _('film\'s genres')

        constraints = [models.UniqueConstraint(fields=['film_work', 'genre'], name='film_work_genre_idx')]


class PersonFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'), null=True)

    class Meta:
        db_table = 'content\'.\'person_film_work'
        verbose_name = _('film crew member')
        verbose_name_plural = _('film crew')

        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='film_work_person_role_idx'),
        ]
