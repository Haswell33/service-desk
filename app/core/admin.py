from django.contrib import admin
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from .models import Ticket, Tenant, User, Priority, Status, Resolution, Transition, Attachment, TransitionAssociation, Type, Label, LabelAssociation, SLAScheme, Board, BoardColumn, BoardColumnAssociation
from django.utils.html import mark_safe
from django.shortcuts import reverse
from django import template

register = template.Library()


class GroupAdminModel(GroupAdmin):
    list_display = ('name', 'role')
    search_fields = ['name', 'role']
    fieldsets = (
        (None, {
            'fields': ('name', 'role')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        })
    )


@admin.register(User)
class UserAdminModel(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_display_name', 'manager', 'admin', 'active', 'get_groups', 'get_icon')
    search_fields = ['username', 'first_name']
    list_filter = ('admin', 'manager', 'active')
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'icon')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('active', 'manager', 'admin')
        }),
        ('Groups', {
            'fields': ('groups',)
        }),
        ('User permissions', {
            'fields': ('permissions',)
        })
    )
    ordering = ['id']
    filter_horizontal = []

    def get_groups(self, instance):
        return [groups.name for groups in instance.groups.all()]
    get_groups.short_description = 'Groups'


@admin.register(Board)
class BoardAdminModel(admin.ModelAdmin):
    list_display = ('name', 'env_type')
    search_fields = ['name', 'env_type']


class BoardColumnAssociationInline(admin.StackedInline):
    model = BoardColumnAssociation
    extra = 0


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


@admin.register(SLAScheme)
class SLAAdminModel(admin.ModelAdmin):
    list_display = ('name', 'reaction_time', 'resolve_time', 'hour_range')
    search_fields = ['name']


@admin.register(Attachment)
class AttachmentAdminModel(admin.ModelAdmin):
    list_display = ('filename', 'file', 'display_size')
    search_fields = ['file']
    fields = ('file',)
    readonly_fields = ('filename',)


@admin.register(Tenant)
class TenantAdminModel(admin.ModelAdmin):
    list_display = ('name', 'get_icon', 'key', 'count', 'sla', 'customers_group', 'operators_group', 'developers_group', 'customers_board', 'operators_board', 'developers_board')
    search_fields = ['name', 'key', 'workflow_developer', 'customers_group', 'operators_group', 'developers_group']


@admin.register(Priority)
class PriorityAdminModel(admin.ModelAdmin):
    list_display = ('name', 'get_icon', 'step')
    search_fields = ['name']


@admin.register(Status)
class StatusAdminModel(admin.ModelAdmin):
    list_display = ('name', 'color_hex', 'resolution')
    search_fields = ['name']


class TransitionAssociationInline(admin.StackedInline):
    model = TransitionAssociation
    extra = 0


@admin.register(Transition)
class TransitionAdminModel(admin.ModelAdmin):
    list_display = ('name', 'full_transition', 'get_types')
    search_fields = ['name', 'src_status', 'dest_status']
    list_filter = ('types', 'src_status', 'dest_status')
    inlines = [TransitionAssociationInline]

    def get_types(self, instance):
        output = ''
        for types in instance.types.all():
            output = output + mark_safe(f'<img src="{settings.MEDIA_URL}/{str(types.icon)}" height="20" width="20" title="{types.name}" alt={types.name}/> ')
        return mark_safe(output)
    get_types.short_description = 'Types'


@admin.register(Resolution)
class ResolutionAdminModel(admin.ModelAdmin):
    display = ('name', 'description')
    search_fields = ['name']


@admin.register(Type)
class TypeAdminModel(admin.ModelAdmin):
    list_display = ('name', 'get_icon', 'env_type')
    search_fields = ['name', 'env_type']


@admin.register(Label)
class LabelAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description')


class LabelAssociationInline(admin.StackedInline):
    model = LabelAssociation
    extra = 0


@admin.register(Ticket)
class TicketAdminModel(admin.ModelAdmin):
    list_display = ('key', 'get_type', 'title', 'get_priority', 'get_status', 'resolution', 'get_reporter', 'get_assignee', 'escalated', 'suspended', 'tenant', 'get_labels', 'created', 'updated')
    search_fields = ['key', 'title', 'tenant__name', 'priority__name', 'status__name', 'resolution__name', 'type__name', 'reporter__username', 'assignee__username']
    list_filter = ('type', 'reporter', 'assignee', 'tenant', 'priority')
    fieldsets = (
        (None, {
            'fields': ('title', 'type', 'priority')
        }),
        ('Users', {
            'fields': ('reporter', 'assignee')
        }),
        ('State', {
            'fields': ('suspended',)
        }),
        ('Data', {
            'fields': ['description']
        }),
    )
    inlines = (LabelAssociationInline, )

    def view_on_site(self, obj):
        return reverse('view_ticket', args=[obj.slug])

    def get_labels(self, instance):
        return [labels.name for labels in instance.labels.all()]
    get_labels.short_description = 'Labels'

    def get_type(self, obj):
        return obj.type.get_icon()
    get_type.short_description = 'Type'

    def get_priority(self, obj):
        return obj.priority.get_icon()
    get_priority.short_description = 'Priority'

    def get_status(self, obj):
        return obj.status.get_colored()
    get_status.short_description = 'Status'

    def get_assignee(self, obj):
        return obj.get_assignee(True)
    get_assignee.short_description = 'Assignee'

    def get_reporter(self, obj):
        return obj.reporter.get_icon()
    get_reporter.short_description = 'Reporter'


admin.site.unregister(Group)
admin.site.register(Group, GroupAdminModel)
AdminSite.index_title = 'Administration'
