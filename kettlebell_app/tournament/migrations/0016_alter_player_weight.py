# Generated by Django 5.1 on 2024-08-29 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0015_kbsquatresult_overallresult_seesawpressresult_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="weight",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
