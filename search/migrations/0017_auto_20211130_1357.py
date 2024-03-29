# Generated by Django 3.2.9 on 2021-11-30 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0016_store_scrape_with_js'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='product_description_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='The css class to know if the product description'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_description_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='The html tag to know if the product description'),
        ),
    ]
