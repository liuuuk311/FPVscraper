# Generated by Django 3.2.9 on 2022-02-11 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0034_store_search_page_param'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingmethod',
            name='is_weight_dependent',
            field=models.BooleanField(default=False, verbose_name='Does the price depend on the shipping weight?'),
        ),
    ]
