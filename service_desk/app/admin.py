from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import Issue, Tenant, Comment, Priority, Status, Resolution, Transition, TransitionAssociation, IssueType, Label, LabelAssociation, SLAScheme, Board, BoardColumn, BoardColumnAssociation
from .forms import IssueForm
from django.utils.html import mark_safe, format_html
from django import template

register = template.Library()

class GroupAdminModel(GroupAdmin):
    list_display = ('name', 'type')
    search_fields = ['name', 'type']
    fieldsets = (
        (None, {
            'fields': ('name', 'type')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        })
    )


class UserAdminModel(GroupAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'icon')
    search_fields = ['username', 'first_name']
    list_filter = ('is_superuser', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'icon')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Groups', {
            'fields': ('groups',)
        }),
        ('User permissions', {
            'fields': ('user_permissions',)
        }),
        ('Dates', {
            'fields': ('last_login', 'date_joined')
        })
    )
    ordering = ['id']
    filter_horizontal = []


@admin.register(Board)
class BoardAdminModel(admin.ModelAdmin):
    list_display = ('name', 'env_type')
    search_fields = ['name', 'env_type']


class BoardColumnAssociationInline(admin.TabularInline):
    model = BoardColumnAssociation


@admin.register(BoardColumn)
class BoardColumnAdminModel(admin.ModelAdmin):
    list_display = ('board', 'column_number', 'column_title', 'get_statuses')
    search_fields = ['board', 'column_title']
    list_filter = ('board', 'column_number')
    inlines = [BoardColumnAssociationInline]

    def get_statuses(self, instance):
        output = ''
        for statuses in instance.statuses.all():
            output = output + ' <div class="status" style="background-color:' + statuses.color + ';">' + statuses.name + '</div>'
        return mark_safe(output)
    get_statuses.short_description = 'Statuses'

'''
@admin.register(BoardColumnAssociation)
class BoardColumnAssociationAdminModel(admin.ModelAdmin):
    list_display = ('column', 'status_color', 'board_name')
    search_fields = ['board', 'column', 'status']
    list_filter = ('column', 'status')
'''


@admin.register(SLAScheme)
class SLAAdminModel(admin.ModelAdmin):
    list_display = ('name', 'reaction_time', 'resolve_time', 'hour_range')
    search_fields = ['name']


@admin.register(Tenant)
class TenantAdminModel(admin.ModelAdmin):
    list_display = ('name', 'icon_img', 'key', 'count', 'sla', 'customers_group', 'operators_group', 'developers_group', 'customers_board', 'operators_board', 'developers_board')
    search_fields = ['name', 'key', 'workflow_developer', 'customers_group', 'operators_group', 'developers_group']


@admin.register(Priority)
class PriorityAdminModel(admin.ModelAdmin):
    list_display = ('name', 'icon_img')
    search_fields = ['name']


@admin.register(Status)
class StatusAdminModel(admin.ModelAdmin):
    list_display = ('name', 'color_hex', 'resolution')
    search_fields = ['name']


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
    list_display = ('name', 'icon_img', 'env_type')
    search_fields = ['name', 'env_type']


@admin.register(Label)
class LabelAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description')


class LabelAssociationInline(admin.TabularInline):
    model = LabelAssociation


@admin.register(Issue)
class IssueAdminModel(admin.ModelAdmin):
    list_display = ('key', 'type_img', 'title', 'priority_img', 'status_color', 'resolution', 'reporter_img_text', 'assignee_img_text', 'escalated', 'suspended', 'tenant', 'get_labels', 'created_datetime', 'updated_datetime')
    search_fields = ['key', 'title', 'tenant', 'priority', 'status', 'resolution', 'type', 'labels', 'reporter', 'assignee']
    list_filter = ('type', 'reporter', 'assignee', 'tenant', 'priority')
    fieldsets = (
        (None, {
            'fields': ('title', 'type', 'priority')
        }),
        ('Users', {
            'fields': ('reporter', 'assignee')
        }),
        ('State', {
            'fields': ('status', 'resolution', 'suspended')
        }),
        ('Data', {
            'fields': ['description', ]
        }),
    )
    inlines = [LabelAssociationInline]

    def get_labels(self, instance):
        return [labels.name for labels in instance.labels.all()]
    get_labels.short_description = 'Labels'

    #get_labels.fget.allow_tags = True
    #get_labels.fget.short_description = 'Address display'


admin.site.unregister(Group)
admin.site.register(Group, GroupAdminModel)
admin.site.unregister(User)
admin.site.register(User, UserAdminModel)
AdminSite.index_title = 'Administration'
