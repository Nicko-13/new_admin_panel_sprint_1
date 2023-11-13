# Generated by Django 4.2.5 on 2023-11-13 10:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('movies', '0004_alter_filmwork_table_alter_genre_table_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personfilmwork',
            name='role',
            field=models.CharField(
                choices=[
                    ('actor', 'actor'),
                    ('director', 'director'),
                    ('writer', 'writer'),
                ],
                null=True,
                verbose_name='role',
            ),
        ),
    ]
