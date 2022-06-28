from django.db.models import Q
import collections


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
    return tickets.order_by(ordering)


def fields_equal(form, attr, ticket_value, form_value):
    def _multiple_choice_field(form, attr): return form.fields.get(attr).widget.attrs.get('multiple')
    def _multiple_choice_fields_equal(list1, list2): return collections.Counter(list1) == collections.Counter(list2)
    if _multiple_choice_field(form, attr):
        form_value_list = form.data.getlist(attr)
        if _multiple_choice_fields_equal([str(value.id) for value in ticket_value], form_value_list):
            return True
    elif str(ticket_value) == str(form_value):
        return True
