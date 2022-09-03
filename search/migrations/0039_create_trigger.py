# Generated by Django 3.2.9 on 2022-03-26 09:44
from django.contrib.postgres.search import SearchVector
from django.db import migrations

def compute_search_vector(apps, schema_editor):
    Product = apps.get_model("search", "Product")
    Product.objects.update(search_vector=SearchVector("name"))

class Migration(migrations.Migration):

    dependencies = [
        ('search', '0038_auto_20220326_0941'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
                CREATE TRIGGER product_update_trigger
                BEFORE INSERT OR UPDATE OF name, search_vector
                ON search_product
                FOR EACH ROW EXECUTE PROCEDURE
                tsvector_update_trigger(
                  search_vector, 'pg_catalog.english', name);

                UPDATE search_product SET search_vector = NULL;
                ''',

            reverse_sql='''
                DROP TRIGGER IF EXISTS product_update_trigger
                ON search_product;
                '''
        ),
        migrations.RunPython(
            compute_search_vector, reverse_code=migrations.RunPython.noop
        ),
    ]