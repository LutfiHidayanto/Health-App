# Generated by Django 4.2.1 on 2024-05-24 07:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthPrediction', '0006_alter_doctorprofile_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='waiting', max_length=50)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_requests', to='healthPrediction.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_requests', to='healthPrediction.patient')),
            ],
        ),
    ]
