# Generated by Django 4.1.3 on 2023-02-04 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snowdays23', '0012_alter_participant_eating_habits_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartyBeast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=16, verbose_name='personal mobile number')),
                ('student_nr', models.CharField(max_length=16, verbose_name='registration number within university')),
                ('bracelet_id', models.CharField(blank=True, max_length=16, null=True, verbose_name='UID of the RFID bracelet associated with this party beast')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='system user associated with this party beast')),
            ],
        ),
    ]
