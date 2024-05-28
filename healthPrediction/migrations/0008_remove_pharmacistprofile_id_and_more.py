# Generated by Django 4.2.1 on 2024-05-24 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthPrediction', '0007_consultationrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pharmacistprofile',
            name='id',
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='pharmacy_city',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='pharmacy_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='pharmacist_photos/'),
        ),
        migrations.AlterField(
            model_name='pharmacistprofile',
            name='pharmacist_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pharmacistprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
