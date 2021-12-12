# Generated by Django 3.2.9 on 2021-12-10 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0026_auto_20211210_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingmethod',
            name='currency',
            field=models.CharField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='EUR', max_length=3, verbose_name='Default Currency'),
        ),
    ]
