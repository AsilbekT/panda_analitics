# Generated by Django 4.2.7 on 2023-12-29 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analitics', '0008_alter_contentlikeunlikecount_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('genre', models.CharField(max_length=255)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('duration_minute', models.IntegerField()),
                ('thumbnail_image', models.CharField(max_length=255)),
                ('widescreen_thumbnail_image', models.CharField(max_length=255)),
                ('content_type', models.CharField(choices=[('movie', 'MOVIE'), ('series', 'SERIES'), ('episode', 'EPISODE')], max_length=100)),
            ],
        ),
    ]