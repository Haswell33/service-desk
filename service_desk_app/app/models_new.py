from django.db import models

PRIORITY_TYPE = models.TextChoices('PriorityType', 'Low Normal High Critical')


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.ForeignKey('Priority', on_delete=models.CASCADE)

    class Meta:
        db_table = 'issue'
        verbose_name = 'issue'
        verbose_name_plural = 'issues'
        ordering = ['id']


class Priority(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10, choices=PRIORITY_TYPE.choices)
    icon

    class Meta:
        db_table = 'issue_priority'
        verbose_name = 'priority'
        verbose_name_plural = 'priorities'
        ordering = ['id']

