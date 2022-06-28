from django.contrib import admin
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import Ticket, Tenant, Comment, Priority, Status, Resolution, Transition, Attachment, AttachmentAssociation, TransitionAssociation, Type, Label, LabelAssociation, SLAScheme, Board, BoardColumn, BoardColumnAssociation
from django.utils.html import mark_safe
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
    list_display = ('name', 'icon_img', 'key', 'count', 'sla', 'customers_group', 'operators_group', 'developers_group', 'customers_board', 'operators_board', 'developers_board')
    search_fields = ['name', 'key', 'workflow_developer', 'customers_group', 'operators_group', 'developers_group']


@admin.register(Priority)
class PriorityAdminModel(admin.ModelAdmin):
    list_display = ('name', 'icon_img', 'step')
    search_fields = ['name']


@admin.register(Status)
class StatusAdminModel(admin.ModelAdmin):
    list_display = ('name', 'color_hex', 'resolution')
    search_fields = ['name']


class TransitionAssociationInline(admin.TabularInline):
    model = TransitionAssociation


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


'''
@admin.register(TransitionAssociation)
class TransitionAssociationAdminModel(admin.ModelAdmin):
    list_display = ('type', 'full_transition')
    search_fields = ['type', 'transition']
    list_filter = ('type', 'transition')
'''


@admin.register(Resolution)
class ResolutionAdminModel(admin.ModelAdmin):
    display = ('name', 'description')
    search_fields = ['name']


@admin.register(Type)
class TypeAdminModel(admin.ModelAdmin):
    list_display = ('name', 'icon_img', 'env_type')
    search_fields = ['name', 'env_type']


@admin.register(Label)
class LabelAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description')


class LabelAssociationInline(admin.TabularInline):
    model = LabelAssociation


@admin.register(Ticket)
class TicketAdminModel(admin.ModelAdmin):
    list_display = ('key', 'type_img', 'title', 'priority_img', 'status_color', 'resolution', 'reporter_img_text', 'assignee_img_text', 'escalated', 'suspended', 'tenant', 'get_labels', 'created_local', 'updated_local')
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
            'fields': ('status', 'resolution', 'suspended')
        }),
        ('Data', {
            'fields': ['description', 'slug']
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
