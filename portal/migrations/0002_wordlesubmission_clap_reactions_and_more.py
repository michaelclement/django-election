# Generated by Django 4.2.7 on 2023-11-25 16:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="wordlesubmission",
            name="clap_reactions",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wordlesubmission",
            name="mind_blown_reactions",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wordlesubmission",
            name="monkey_reactions",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wordlesubmission",
            name="sad_reactions",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wordlesubmission",
            name="wow_reactions",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
