from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
#from django.contrib.sites.models import Site

from app.models import Issue, Tenant, Comment, Priority, Status, Resolution, Type, Label, SLA, Workflow


#class StatusAdminForm(admin.ModelAdmin):
#    pass


@admin.register(SLA)
class SLAAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'reaction_time', 'resolve_time', 'hour_range')


@admin.register(Workflow)
class WorkflowAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'pattern')


@admin.register(Tenant)
class TenantAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'key', 'count', 'sla', 'workflow_operator', 'workflow_developer', 'customers_group', 'operators_group', 'developers_group', 'icon')


@admin.register(Priority)
class PriorityAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon_tag')


@admin.register(Status)
class StatusAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'status_type', 'color')
    class Meta:
        #model = Status
        #fields = (('id', 'name', 'type'), 'description')
        fieldsets = (
            (None, {
                'fields': ('id', 'name')
            }),
            ('Advanced options', {
                'classes': ('collapse',),
                'fields': ('description', 'type'),
            }),
        )


@admin.register(Resolution)
class ResolutionAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Type)
class TypeAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'icon')


@admin.register(Label)
class LabelAdminModel(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Issue)
class IssueAdminModel(admin.ModelAdmin):
    list_display = ('id', 'title', 'key', 'tenant', 'priority', 'status', 'resolution', 'type', 'label', 'reporter', 'assignee', 'escalated', 'suspended', 'created', 'updated')


AdminSite.index_title = 'Administration'
admin.site.site_title = 'nowy title'
admin.site.site_header = 'nowy header'
# admin.site.unregister(Group)