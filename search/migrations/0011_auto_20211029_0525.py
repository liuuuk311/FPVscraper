# Generated by Django 3.0.8 on 2021-10-29 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0010_shippingmethod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingmethod',
            name='min_price_free_shipping',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Minimum price to get free shipping'),
        ),
    ]
