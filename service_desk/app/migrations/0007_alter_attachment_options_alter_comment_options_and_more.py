# Generated by Django 4.0.4 on 2022-05-21 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_status_type_type_alter_issue_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'ordering': ['id'], 'verbose_name': 'attachment', 'verbose_name_plural': 'attachments'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['id'], 'verbose_name': 'comment', 'verbose_name_plural': 'comments'},
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['id'], 'verbose_name': 'issue', 'verbose_name_plural': 'issues'},
        ),
        migrations.AlterModelOptions(
            name='issueassociation',
            options={'ordering': ['id'], 'verbose_name': 'link', 'verbose_name_plural': 'links'},
        ),
        migrations.AlterModelOptions(
            name='label',
            options={'ordering': ['id'], 'verbose_name': 'label', 'verbose_name_plural': 'labels'},
        ),
        migrations.AlterModelOptions(
            name='priority',
            options={'ordering': ['id'], 'verbose_name': 'priority', 'verbose_name_plural': 'priorities'},
        ),
        migrations.AlterModelOptions(
            name='resolution',
            options={'ordering': ['id'], 'verbose_name': 'resolution', 'verbose_name_plural': 'resolutions'},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['id'], 'verbose_name': 'status', 'verbose_name_plural': 'statuses'},
        ),
        migrations.AlterModelOptions(
            name='tenant',
            options={'ordering': ['id'], 'verbose_name': 'tenant', 'verbose_name_plural': 'tenants'},
        ),
        migrations.AlterModelOptions(
            name='type',
            options={'ordering': ['id'], 'verbose_name': 'issue type', 'verbose_name_plural': 'issue types'},
        ),
        migrations.AlterModelOptions(
            name='workflow',
            options={'verbose_name': 'workflow', 'verbose_name_plural': 'workflows'},
        ),
        migrations.AlterField(
            model_name='label',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='priority',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='resolution',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='status',
            name='Type',
            field=models.CharField(choices=[('SD', 'Service Desk'), ('software', 'Software')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='type',
            name='Type',
            field=models.CharField(choices=[('SD', 'Service Desk'), ('software', 'Software')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='type',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
