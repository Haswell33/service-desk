# Generated by Django 3.2.13 on 2022-06-26 22:34

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20220626_1541'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auditlog',
            options={'ordering': ['-created'], 'verbose_name': 'audit log', 'verbose_name_plural': 'audit logs'},
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=app.models.get_upload_path, validators=[app.models.validate_file_extension]),
        ),
    ]
