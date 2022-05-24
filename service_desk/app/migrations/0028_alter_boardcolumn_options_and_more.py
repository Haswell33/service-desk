# Generated by Django 4.0.4 on 2022-05-23 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_board_boardcolumn_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boardcolumn',
            options={'ordering': ['column_number'], 'verbose_name': 'board column', 'verbose_name_plural': 'board columns'},
        ),
        migrations.RenameField(
            model_name='boardcolumn',
            old_name='title',
            new_name='column_title',
        ),
        migrations.RemoveField(
            model_name='boardcolumn',
            name='number',
        ),
        migrations.AddField(
            model_name='boardcolumn',
            name='column_number',
            field=models.IntegerField(default=1),
        ),
    ]
