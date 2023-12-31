# Generated by Django 4.2.5 on 2023-11-01 10:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('movies', '0002_genrefilmwork_modified_personfilmwork_modified_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='genrefilmwork',
            name='film_work_genre_idx',
        ),
        migrations.RemoveIndex(
            model_name='personfilmwork',
            name='film_work_person_role_idx',
        ),
        migrations.AddConstraint(
            model_name='genrefilmwork',
            constraint=models.UniqueConstraint(fields=('film_work', 'genre'), name='film_work_genre_idx'),
        ),
        migrations.AddConstraint(
            model_name='personfilmwork',
            constraint=models.UniqueConstraint(
                fields=('film_work', 'person', 'role'), name='film_work_person_role_idx'
            ),
        ),
    ]
