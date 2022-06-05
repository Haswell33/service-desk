from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import Issue, Tenant, Comment, Priority, Status, Resolution, Transition, TransitionAssociation, IssueType, Label, SLAScheme, Board, BoardColumn, BoardColumnAssociation


class GroupAdminModel(GroupAdmin):
    list_display = ('name', 'type')
    search_fields = ['name', 'type']


@admin.register(Board)
class BoardAdminModel(admin.ModelAdmin):
    list_display = ('name', 'env_type')
    search_fields = ['name', 'env_type']


@admin.register(BoardColumn)
class BoardColumnAdminModel(admin.ModelAdmin):
    list_display = ('board', 'column_number', 'column_title')
    search_fields = ['board', 'column_title']
    list_filter = ('board', 'column_number')


@admin.register(BoardColumnAssociation)
class BoardColumnAssociationAdminModel(admin.ModelAdmin):
    list_display = ('column', 'status_colored', 'board')
    search_fields = ['board', 'column', 'status']
    list_filter = ('column', 'status')


@admin.register(SLAScheme)
class SLAAdminModel(admin.ModelAdmin):
    list_display = ('name', 'reaction_time', 'resolve_time', 'hour_range')
    search_fields = ['name']


@admin.register(Tenant)
class TenantAdminModel(admin.ModelAdmin):
    list_display = ('name', 'key', 'count', 'sla', 'customers_group', 'operators_group', 'developers_group', 'customers_board', 'operators_board', 'developers_board', 'icon_img_admin')
    search_fields = ['name', 'key', 'workflow_developer', 'customers_group', 'operators_group', 'developers_group']


@admin.register(Priority)
class PriorityAdminModel(admin.ModelAdmin):
    list_display = ('name', 'icon_img_admin')
    search_fields = ['name']


@admin.register(Status)
class StatusAdminModel(admin.ModelAdmin):
    list_display = ('name', 'resolution', 'color_hex')
    search_fields = ['name']
    # list_filter = ('step', 'forward_transition')


@admin.register(Transition)
class TransitionAdminModel(admin.ModelAdmin):
    list_display = ('name', 'full_transition')
    search_fields = ['name', 'src_status', 'dest_status']
    list_filter = ('name', 'src_status', 'dest_status')


@admin.register(TransitionAssociation)
class TransitionAssociationAdminModel(admin.ModelAdmin):
    list_display = ('issue_type', 'full_transition')
    search_fields = ['issue_type', 'transition']
    list_filter = ('issue_type', 'transition')


@admin.register(Resolution)
class ResolutionAdminModel(admin.ModelAdmin):
    display = ('name', 'description')
    search_fields = ['name']


@admin.register(IssueType)
class IssueTypeAdminModel(admin.ModelAdmin):
    list_display = ('name', 'env_type', 'icon_img_admin')
    search_fields = ['name', 'env_type']


@admin.register(Label)
class LabelAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Issue)
class IssueAdminModel(admin.ModelAdmin):
    list_display = ('key', 'title', 'tenant', 'priority', 'status', 'resolution', 'full_issue_type', 'label', 'reporter', 'assignee', 'escalated', 'suspended', 'created', 'updated')
    search_fields = ['key', 'title', 'tenant', 'priority', 'status', 'resolution', 'type', 'label', 'reporter', 'assignee']


#@admin.register(TransitionAssociation)
#class StatusAssociationAdminModel(admin.ModelAdmin):
#    list_display = ('issue_type', 'status', 'status_step')
#    search_fields = ['status', 'issue_type']
#    list_filter = ('issue_type', 'status')


admin.site.unregister(Group)
admin.site.register(Group, GroupAdminModel)
AdminSite.index_title = 'Administration'
admin.site.site_title = 'nowy title'
admin.site.site_header = 'nowy header'
# admin.site.unregister(Group)