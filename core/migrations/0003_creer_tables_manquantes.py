from django.db import migrations
from django.apps import apps as global_apps


def creer_tables_manquantes(apps, schema_editor):
    connection = schema_editor.connection
    tables_existantes = connection.introspection.table_names()
    app_config = global_apps.get_app_config('core')
    for model in app_config.get_models():
        if model._meta.db_table not in tables_existantes:
            schema_editor.create_model(model)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_fix_colonnes_manquantes'),
    ]

    operations = [
        migrations.RunPython(creer_tables_manquantes, migrations.RunPython.noop),
    ]