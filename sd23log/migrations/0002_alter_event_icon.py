# Generated by Django 4.1.3 on 2023-02-15 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sd23log', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='icon',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='id of the icon resource for this event'),
        ),
    ]
