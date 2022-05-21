from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
#from django.contrib.sites.models import Site

from app.models import Issue, Tenant, Comment, Priority, Status, Resolution, Type, Label, SLA, Workflow

class StatusAdminForm():
    pass

class StatusAdminModel(admin.ModelAdmin):
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

AdminSite.index_title = 'Administration'
admin.site.register(Issue)
admin.site.register(Status, StatusAdminModel)
admin.site.register(Type)
admin.site.register(Resolution)
admin.site.register(Label)
admin.site.register(SLA)
admin.site.register(Workflow)
admin.site.register(Priority)
admin.site.register(Tenant)
admin.site.site_title = 'nowy title'
admin.site.site_header = 'nowy header'
# admin.site.unregister(Group)