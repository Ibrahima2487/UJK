from django.db import migrations
from django.apps import apps as global_apps


def synchroniser(apps, schema_editor):
    connection = schema_editor.connection
    tables_existantes = connection.introspection.table_names()
    app_config = global_apps.get_app_config('core')

    for model in app_config.get_models():
        table = model._meta.db_table

        if table not in tables_existantes:
            # Table entière manquante -> on la crée
            schema_editor.create_model(model)
            continue

        # Table existante -> on vérifie les colonnes une par une
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(cursor, table)
        colonnes_existantes = {col.name for col in description}

        for field in model._meta.local_fields:
            if field.column not in colonnes_existantes:
                try:
                    schema_editor.add_field(model, field)
                except Exception as e:
                    print(f"Impossible d'ajouter {table}.{field.column} : {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_creer_tables_manquantes'),
    ]

    operations = [
        migrations.RunPython(synchroniser, migrations.RunPython.noop),
    ]