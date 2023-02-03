# Generated by Django 3.2.16 on 2023-02-02 17:02

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialrecipe', '0012_alter_recipes_excerpt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeimages',
            name='recipe_image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]