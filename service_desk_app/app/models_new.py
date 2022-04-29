from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib import admin
from crum import get_current_user
from datetime import datetime
from . import utils

PRIORITY_TYPE = models.TextChoices('PriorityType', 'Low Normal High Critical')


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, help_text='Summarize the issue')
    key = models.CharField(max_length=255)
    description = models.TextField(verbose_name='Description', blank=True, help_text='The content of the issue')
    priority = models.ForeignKey('Priority', on_delete=models.CASCADE)
    status = models.ForeignKey('Status', on_delete=models.CASCADE)
    resolution = models.ForeignKey('Resolution', on_delete=models.CASCADE, blank=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    label = models.ForeignKey('Label', on_delete=models.CASCADE, blank=True)
    sla_pattern = models.ForeignKey('SLA', on_delete=models.CASCADE)
    reporter = models.ForeignKey('User', on_delete=models.CASCADE)
    assignee = models.ForeignKey('User', on_delete=models.CASCADE, blank=True)
    escalated = models.BooleanField(verbose_name='Escalated', default=False)
    suspended = models.BooleanField(verbose_name='Suspended', default=False)
    created = models.DateTimeField(verbose_name='Created', blank=True, help_text='Date when issue has been created')
    updated = models.DateTimeField(verbose_name='Updated', blank=True, help_text='Date when issue has been recently changed')

    class Meta:
        db_table = 'issue'
        # verbose_name = 'issue'
        # verbose_name_plural = 'issues'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.reporter = get_current_user()
        # if not self.priority:
        #    self.priority = 3
        self.modified = datetime.now()
        if len(self.title) > 200:
            self.title = self.title[:197] + "..."
        super().save(*args, **kwargs)


class Priority(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/priorities')

    class Meta:
        db_table = 'issue_priority'
        ordering = ['id']


class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=7)


class Resolution(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)


class Type(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/issuetypes')


class Label(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)


class SLA(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    reaction_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to reaction in minutes before escalation')
    resolve_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to resolve in minutes before escalation')
    hour_range = models.CharField(max_length=5)
