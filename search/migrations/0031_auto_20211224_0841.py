# Generated by Django 3.2.9 on 2021-12-24 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0030_importquery_products_clicks'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='affiliate_id',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='The affiliate id'),
        ),
        migrations.AddField(
            model_name='store',
            name='affiliate_query_param',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='The affiliate query parameter'),
        ),
        migrations.AlterField(
            model_name='importquery',
            name='priority',
            field=models.IntegerField(choices=[(0, 'Low'), (1, 'Medium'), (2, 'High')], default=1, verbose_name='Import Priority'),
        ),
    ]
