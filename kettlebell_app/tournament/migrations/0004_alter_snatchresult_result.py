# Generated by Django 5.1 on 2024-09-01 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0003_remove_player_see_saw_press_weight_left_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="snatchresult",
            name="result",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
