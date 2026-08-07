from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_utilisateur
                ADD COLUMN IF NOT EXISTS en_ligne boolean NOT NULL DEFAULT false;
                ALTER TABLE core_utilisateur
                ADD COLUMN IF NOT EXISTS derniere_activite timestamp with time zone NULL;
            """,
            reverse_sql="""
                ALTER TABLE core_utilisateur DROP COLUMN IF EXISTS en_ligne;
                ALTER TABLE core_utilisateur DROP COLUMN IF EXISTS derniere_activite;
            """,
            state_operations=[
                migrations.AddField(
                    model_name='utilisateur',
                    name='en_ligne',
                    field=__import__('django.db.models', fromlist=['BooleanField']).BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='utilisateur',
                    name='derniere_activite',
                    field=__import__('django.db.models', fromlist=['DateTimeField']).DateTimeField(null=True, blank=True),
                ),
            ],
        ),
    ]