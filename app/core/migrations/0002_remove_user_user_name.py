# Generated by Django 5.1.2 on 2024-10-28 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="user_name",
        ),
    ]