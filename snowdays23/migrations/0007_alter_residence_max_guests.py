# Generated by Django 4.1.3 on 2023-01-10 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snowdays23', '0006_residence_city_residence_postal_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='residence',
            name='max_guests',
            field=models.IntegerField(default=4, verbose_name='maximum number of guests this location can hold at once'),
        ),
    ]
