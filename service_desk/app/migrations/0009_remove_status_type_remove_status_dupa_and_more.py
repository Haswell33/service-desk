# Generated by Django 4.0.4 on 2022-05-22 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_status_dupa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='Type',
        ),
        migrations.RemoveField(
            model_name='status',
            name='dupa',
        ),
        migrations.AddField(
            model_name='status',
            name='status_type',
            field=models.CharField(choices=[('SD', 'Service Desk'), ('software', 'Software')], max_length=50, null=True, verbose_name='Type'),
        ),
    ]
