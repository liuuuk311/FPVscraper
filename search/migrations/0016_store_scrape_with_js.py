# Generated by Django 3.0.8 on 2021-11-28 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0015_auto_20211125_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='scrape_with_js',
            field=models.BooleanField(default=False, verbose_name='Use JS when scraping'),
        ),
    ]
