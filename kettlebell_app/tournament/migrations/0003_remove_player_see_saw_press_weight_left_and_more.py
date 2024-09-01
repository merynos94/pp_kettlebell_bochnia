# Generated by Django 5.1 on 2024-09-01 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0002_alter_overallresult_kb_squat_points_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="player", name="see_saw_press_weight_left",),
        migrations.RemoveField(model_name="player", name="see_saw_press_weight_right",),
        migrations.RemoveField(model_name="seesawpressresult", name="result_left",),
        migrations.RemoveField(model_name="seesawpressresult", name="result_right",),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_left_1",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_left_2",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_left_3",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_right_1",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_right_2",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="see_saw_press_weight_right_3",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_left_1",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_left_2",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_left_3",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_right_1",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_right_2",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="seesawpressresult",
            name="result_right_3",
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name="BestSeeSawPressResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("best_left", models.FloatField(default=0)),
                ("best_right", models.FloatField(default=0)),
                (
                    "player",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tournament.player",
                    ),
                ),
            ],
        ),
    ]
