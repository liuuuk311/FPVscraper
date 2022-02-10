# Generated by Django 3.2.9 on 2022-02-10 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0032_auto_20211224_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='product_description_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_image_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_is_available_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_name_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_price_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_thumb_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_variations_css_is_class',
            field=models.BooleanField(default=True, verbose_name='CSS is a class'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_description_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="CSS class/id for Product's description"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_description_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='HTML tag to know if the product description'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_image_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="CSS class/id for Product's image"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_image_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='HTML tag for the main image of the product'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_is_available_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='CSS class/id to know if the product is available'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_is_available_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='HTML tag to know if the product is available'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_name_class',
            field=models.CharField(max_length=64, verbose_name="CSS class/id for Product's name"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_name_tag',
            field=models.CharField(max_length=64, verbose_name="HTML tag for the product's name"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_price_class',
            field=models.CharField(max_length=64, verbose_name="CSS class/id for Product's price"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_price_tag',
            field=models.CharField(max_length=64, verbose_name="HTML tag for the product's price"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_thumb_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="CSS class/id for Product's thumbnail"),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_thumb_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='HTML tag for the thumbnail images of the product'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_variations_class',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='CSS class/id to know if the product has variations'),
        ),
        migrations.AlterField(
            model_name='store',
            name='product_variations_tag',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='HTML tag to know if the product has variations'),
        ),
    ]
