from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_identifier", "0002_alter_identification_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="identification",
            name="model_name",
            field=models.CharField(default="SpeciesNet 4.0.3a", max_length=100),
        ),
    ]
