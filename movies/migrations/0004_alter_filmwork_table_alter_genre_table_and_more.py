# Generated by Django 4.2.5 on 2023-11-01 11:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('movies', '0003_remove_genrefilmwork_film_work_genre_idx_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='filmwork',
            table='content"."film_work',
        ),
        migrations.AlterModelTable(
            name='genre',
            table='content"."genre',
        ),
        migrations.AlterModelTable(
            name='genrefilmwork',
            table='content"."genre_film_work',
        ),
        migrations.AlterModelTable(
            name='person',
            table='content"."person',
        ),
        migrations.AlterModelTable(
            name='personfilmwork',
            table='content"."person_film_work',
        ),
    ]
