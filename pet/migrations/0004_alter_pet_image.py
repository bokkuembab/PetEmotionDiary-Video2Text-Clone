# Generated by Django 4.2 on 2023-06-19 06:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pet", "0003_pet_image_pet_is_neutered"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pet",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="pet_images/"),
        ),
    ]
