# Generated by Django 3.2.9 on 2021-12-03 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0018_auto_20211203_0615'),
    ]

    operations = [
        migrations.AddField(
            model_name='continent',
            name='name_en',
            field=models.CharField(max_length=128, null=True, verbose_name='The name of the continent'),
        ),
        migrations.AddField(
            model_name='continent',
            name='name_it',
            field=models.CharField(max_length=128, null=True, verbose_name='The name of the continent'),
        ),
    ]
