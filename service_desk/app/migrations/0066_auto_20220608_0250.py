# Generated by Django 3.2.13 on 2022-06-08 00:50

from django.db import migrations, models
import django_quill.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0065_alter_issue_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='associations',
            field=models.ManyToManyField(related_name='_app_issue_associations_+', through='app.IssueAssociation', to='app.Issue'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=django_quill.fields.QuillField(blank=True, help_text='Describe the issue', null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='status',
            name='transitions',
            field=models.ManyToManyField(related_name='_app_status_transitions_+', through='app.Transition', to='app.Status'),
        ),
    ]
