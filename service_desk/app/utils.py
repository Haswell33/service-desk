from django.conf import settings
from django.db.models import Q
from .models import Tenant, TenantSession, IssueType, Issue, IssueAssociation, Status, Board, BoardColumn, BoardColumnAssociation, TransitionAssociation, AuditLog, Attachment, AttachmentAssociation
from collections import namedtuple
import json
import logging
from django.core.files.base import ContentFile
import collections

logger = logging.getLogger(__name__)


def get_client_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def add_audit_log(request, obj, message):
    return AuditLog.objects.create(
        user=request.user,
        object=obj.id,
        object_type=obj._meta.model.__name__,
        session=request.session.session_key,
        ip_address=get_client_ip_address(request),
        url=request.path,
        message=f'object {obj._meta.model.__name__} with instance id {obj.id} {message}').message


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)


def get_board_columns(user):
    active_tenant_session = get_active_tenant_session(user)
    if active_tenant_session.user_type == settings.CUST_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.customers_board.id)
    elif active_tenant_session.user_type == settings.OPER_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.operators_board.id)
    elif active_tenant_session.user_type == settings.DEV_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.developers_board.id)
    return BoardColumn.objects.filter(board=board)


def get_board_columns_assocations(board_columns):
    board_columns_associations = []
    for board_column in board_columns:
        board_columns_associations.append(BoardColumnAssociation.objects.filter(column=board_column))
    return board_columns_associations


def get_tenant_by_group_type(group_type, group_id):
    try:
        if group_type == settings.CUST_TYPE:
            return Tenant.objects.get(customers_group=group_id)
        elif group_type == settings.OPER_TYPE:
            return Tenant.objects.get(operators_group=group_id)
        elif group_type == settings.DEV_TYPE:
            return Tenant.objects.get(developers_group=group_id)
    except Tenant.DoesNotExists:
        return None


def tenant_session(user):  # checks if any tenant session exists for specific user
    try:
        TenantSession.objects.filter(user=user)
        return True
    except TenantSession.DoesNotExist:
        return False


def active_tenant_session(user):  # checks if any active tenant session exists for specific user
    try:
        get_active_tenant_session(user)
        return True
    except TenantSession.DoesNotExist:
        return False


def tenant_session_exists(tenant, user):  # check if specific tenant session assigned to provided user exists in database
    if TenantSession.objects.filter(tenant=tenant, user=user):
        return True
    else:
        return False


def add_tenant_session(tenant, user, user_type):  # creates tenant session record in database for selected user
    TenantSession.objects.create(
        user_type=user_type,
        tenant=tenant,
        user=user)


def clear_tenant_session(user):  # delete all tenant session data for selected user (during log out)
    TenantSession.objects.filter(user=user).delete()


def set_active_tenant(tenant, request):  # change tenant state to active based on data in cookies or choose default if no data in cookies
    def _set_active_tenant(tenant, request):
        tenant_session = TenantSession.objects.get(tenant=tenant, user=request.user)
        tenant_session.active = True
        tenant_session.save()
        logger.info(add_audit_log(request, tenant_session, f'field update "active" to "{tenant_session.active}"'))

    tenant_cookie = get_tenant_cookie_name(request.user)
    if request.COOKIES.get(tenant_cookie) is None and not TenantSession.objects.filter(active=True, user=request.user):
        _set_active_tenant(tenant, request)
    elif request.COOKIES.get(tenant_cookie) == str(tenant.id):
        _set_active_tenant(tenant, request)


def get_active_tenant(user):
    return Tenant.objects.get(id=get_active_tenant_session(user).tenant.id)


def get_active_tenant_session(user):
    return TenantSession.objects.get(active=True, user=user)


def get_all_user_tenant_sessions(user):
    return TenantSession.objects.filter(user=user.id)


def get_tenant_cookie_name(user):
    return f'active_tenant_id_{str(user.id)}'


def get_active_tenant_tickets(user, only_open):
    active_tenant = get_active_tenant(user)
    if only_open:  # returns tickets where resolution is null
        return Issue.objects.filter(tenant=active_tenant.id, resolution__isnull=True)
    else:
        return Issue.objects.filter(tenant=active_tenant.id)


def filter_tickets(tickets, filters):
    for filter in filters:
        filter_value = filters[filter]
        if filter_value == 'None':
            tickets = tickets.filter(**{filter + '__isnull': True})
        elif filter_value and not isinstance(filter_value, list):
            tickets = tickets.filter(**{filter: filter_value})
        elif isinstance(filter_value, list):
            try:
                tickets = tickets.filter(**{filter + '__in': filter_value})
            except ValueError:
                if len(filter_value) == 1:
                    tickets = tickets.filter(**{filter + '__isnull': True})
                else:
                    filter_values_not_null = []
                    for filtering_value in filter_value:
                        if filtering_value != 'None':
                            filter_values_not_null.append(filtering_value)
                    tickets = tickets.filter(Q(**{filter + '__in': filter_values_not_null}) | Q(**{filter + '__isnull': True}))
    return tickets


def order_tickets(tickets, ordering):
    tickets = tickets.order_by(ordering)
    return tickets


def get_transitions(object):
    return TransitionAssociation.objects.filter((Q(transition__src_status=object.status) | Q(transition__src_status__isnull=True)) & Q(type=object.type))


def create_ticket(form, request):
    tenant = get_active_tenant(request.user)
    files = request.FILES.getlist('attachments')
    new_ticket = form.save(commit=False)  # create instance, but do not save
    new_ticket.key = f'{tenant.key}-{tenant.count + 1}'
    new_ticket.tenant = tenant
    new_ticket.status = get_initial_status(get_env_type(new_ticket.type.id))
    new_ticket.save()  # create ticket
    if files:
        new_ticket = add_attachments(files, new_ticket, request)
    logger.info(add_audit_log(request, new_ticket, f'"{new_ticket}" create'))
    tenant.count += 1
    tenant.save()
    form.save_m2m()


def add_attachments(attachments, ticket, request):
    for attachment in attachments:
        new_attachment = Attachment(directory=ticket.slug)
        new_attachment.file.save(attachment.name, ContentFile(attachment.read()))
        logger.info(add_audit_log(request, new_attachment, f'create attachment "{new_attachment}"'))
        ticket.attachments.add(new_attachment.id)
        logger.info(add_audit_log(request, ticket, f'attachment "{new_attachment}" upload to {ticket}'))
    return ticket


def delete_attachment(ticket, attachment, request):
    attachment_association = AttachmentAssociation.objects.filter(attachment=attachment.id, issue=ticket.id)
    if attachment_association:
        AttachmentAssociation.objects.filter(attachment=attachment.id, issue=ticket.id).delete()
        logger.info(add_audit_log(request, ticket, f'delete attachment "{attachment}"'))
        Attachment.objects.get(id=attachment.id).delete()
        logger.info(add_audit_log(request, attachment, f'delete "{attachment}"'))
        return True
    else:
        return False


def add_relations(relations, ticket, request):
    for relation in relations:
        print(relation)
        related_ticket = Issue.objects.get(id=relation)
        print(related_ticket)
        print(ticket.id)
        print(ticket)
        new_relation = IssueAssociation(src_issue=ticket, dest_issue=related_ticket)
        new_relation.save()
        # new_attachments.append(new_attachment.id)
        logger.info(add_audit_log(request, new_relation, f'create relation "{new_relation}"'))
        #related_ticket.add(new_relation.id)
        #ticket.relations.add(new_relation.id)
        logger.info(add_audit_log(request, ticket, f'relation "{new_relation}" add to {ticket}'))
    return ticket


def update_ticket(form, request):  # TO DO - change attr value
    instance_updated = None
    fields = form.initial
    instance = form.instance  # ticket
    for attr in fields:
        attr_value = fields[attr]
        form_attr_value = form.data.get(attr)
        if multiple_choice_field(form, attr):  # check if multiple choice field
            form_attr_value_list = form.data.getlist(attr)
            if not multiple_choice_field_equal([str(value.id) for value in attr_value], form_attr_value_list):
                instance_updated = update_ticket_field(instance, instance_updated, attr, form_attr_value, form, request)
        else:
            if str(attr_value) != str(form_attr_value):
                instance_updated = update_ticket_field(instance, instance_updated, attr, form_attr_value, form, request)
    return instance_updated


def update_ticket_field(instance, instance_updated, attr, form_attr_value, form, request):
    if instance_updated is None:
        instance_updated = instance
    try:  # if common field
        setattr(instance, attr, form_attr_value)
    except ValueError:  # if ForeignKey field
        form_attr_value = form.fields.get(attr)._queryset.get(id=form_attr_value)
        setattr(instance, attr, form_attr_value)
    except TypeError:  # if ManyToMany field
        form_attr_value = form.data.getlist(attr)
        instance.getattr(attr).set(form_attr_value)
    finally:
        instance_updated.save()
        logger.info(add_audit_log(request, instance_updated, f'field update "{attr}" to "{form_attr_value}"'))
        return instance_updated


def set_ticket_status(transition_association, context_transition_associations, ticket, request):
    for context_transition_association in context_transition_associations:
        if context_transition_association.id == transition_association.id and ticket.type == transition_association.type:
            ticket.status = transition_association.transition.dest_status
            ticket.resolution = transition_association.transition.dest_status.resolution
            ticket.save()
            logger.info(add_audit_log(request, ticket, f'field update "{ticket.status._meta.verbose_name}" to "{ticket.status}"'))
            return ticket
    return None


def set_ticket_assignee(user, ticket, request):
    ticket.assignee = user
    ticket.save()
    logger.info(add_audit_log(request, ticket, f'field update "assignee" to "{ticket.assignee}"'))
    return ticket


def set_ticket_suspend(ticket, request):
    if ticket.suspended:
        ticket.suspended = False
    else:
        ticket.suspended = True
    ticket.save()
    logger.info(add_audit_log(request, ticket, f'field update "suspended" to "{ticket.suspended}"'))
    return ticket


def change_active_tenant(tenant_id, user):
    active_tenant_session = get_active_tenant_session(user)
    active_tenant_session.active = False
    active_tenant_session.save()
    curr_tenant_session = TenantSession.objects.get(tenant=tenant_id, user=user.id)
    curr_tenant_session.active = True
    curr_tenant_session.save()


def convert_query_dict_to_dict(query_dict):
    new_dict = dict()
    for key, value in dict(query_dict).items():  # QueryDict -> common python dict
        new_dict[key] = value
    return new_dict


def multiple_choice_field(form, attr): return form.fields.get(attr).widget.attrs.get('multiple')
def multiple_choice_field_equal(list1, list2): return collections.Counter(list1) == collections.Counter(list2)
def get_env_type(issue_type_id): return IssueType.objects.get(id=issue_type_id).env_type
def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())
