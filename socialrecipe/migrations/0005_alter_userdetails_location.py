# Generated by Django 3.2.16 on 2022-12-31 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialrecipe', '0004_auto_20221231_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetails',
            name='location',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]