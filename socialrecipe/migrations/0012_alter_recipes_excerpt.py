# Generated by Django 3.2.16 on 2023-02-02 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialrecipe', '0011_auto_20230201_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='excerpt',
            field=models.TextField(),
        ),
    ]
