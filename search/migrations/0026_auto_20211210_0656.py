# Generated by Django 3.2.9 on 2021-12-10 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0025_shippingmethod_is_vat_included'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=128, verbose_name='The name of the shipping zone')),
                ('ship_to', models.ManyToManyField(to='search.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='shippingmethod',
            name='shipping_rule',
        ),
        migrations.DeleteModel(
            name='ShippingRule',
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='shipping_zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_methods', to='search.shippingzone'),
        ),
    ]
