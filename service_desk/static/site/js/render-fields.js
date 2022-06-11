function renderFields(page) {
    switch(page) {
        case 'admin':
            adminFields()
            break
        case 'create-ticket':
            createTicketFields()
            break
        default:
            console.error('not found provided page, can not load select2 fields')
    }
}

function adminFields() {
    renderField('#id_type', 'Select an issue type', true, false, false, -1)
    renderField('#id_priority', 'Select a priority', true, false, false, -1)
    renderField('#id_assignee', 'Select a assignee', true, true, false, 0)
    renderField('#id_reporter', 'Select a reporter', true, false, false, 0)
    renderField('#id_status', 'Select a status', false, false, false, -1)
    renderField('#id_resolution', 'Select a resolution', false, true, false, -1)

    renderField('#id_src_status', 'Select a source status', false, false, false, -1)
    renderField('#id_dest_status', 'Select a destination status', false, false, false, -1)


    renderField('#id_issue_type', 'Select an issue type', true, false, false, -1)
    renderField('#id_transition', 'Select a destination status', false, false, false, -1)


    renderField('#id_sla', 'Select a destination status', false, false, false, -1)
    renderField('#id_customers_group', 'Select a customers group', false, true, false, 0)
    renderField('#id_operators_group', 'Select a developers group', false, true, false, 0)
    renderField('#id_developers_group', 'Select a operators group', false, true, false, 0)
    renderField('#id_customers_board', 'Select a default board for customers', false, true, false, 0)
    renderField('#id_operators_board', 'Select a default board for operators', false, true, false, 0)
    renderField('#id_developers_board', 'Select a default board for developers', false, true, false, 0)

    renderField('#id_env_type', 'Select a purpose of this object', false, true, false, -1)
    renderField('#id_board', 'Select a assigned board', false, false, false, 0)
    renderField('#id_column', 'Select a column where status will be displayed', false, false, false, 0)

    renderField('select[name=action]', 'Select a bulk action for selected rows', false, true, false, -1)
}

function createTicketFields(){
    renderField('#id_type', 'Select an issue type', true, false, false, -1)
    renderField('#id_priority', 'Select a priority', true, false, false, -1)
    renderField('#id_assignee', 'Select a priority', true, true, false, 0)
    renderField('#id_labels', 'Categorize a ticket', false, true, true, 0)
}

function renderField(htmlTag, placeholderText, icon, allowClear, multiple, minResults) {
    $(htmlTag).select2({
        templateResult: function (option)  {
            if (icon)
                return renderIconOption(option)
            else
                return option.text
        },
        templateSelection: function (option)  {
            if (icon)
                return renderIconOption(option)
            else
                return option.text
        },
        placeholder: placeholderText,
        allowClear: allowClear,
        multiple: multiple,
        minimumResultsForSearch: minResults
    })
}

function select2(){
    $('#id_type').select2({
        templateResult: function (option)  {
            return renderIconOption(option)
        },
        templateSelection: function (option)  {
            return renderIconOption(option)
        },
        placeholder: 'Select an issue type',
        minimumResultsForSearch: -1
    })
    $('#id_priority').select2({
        templateResult: function (option)  {
            return renderIconOption(option)
        },
        templateSelection: function (option)  {
            return renderIconOption(option)
        },
        placeholder: 'Select an priority',
        minimumResultsForSearch: -1
    })
    $('#id_assignee').select2({
        templateResult: function (option) {
            return renderIconOption(option)
        },
        templateSelection: function (option) {
            return renderIconOption(option)
            },
        placeholder: 'Select a person whose ticket will be assigned',
        allowClear: true
    })
    $('#id_reporter').select2({
        templateResult: function (option) {
            return renderIconOption(option)
        },
        templateSelection: function (option) {
            return renderIconOption(option)
            },
        placeholder: 'Select a reporter',
        allowClear: true
    })
    $('#id_labels').select2({
        placeholder: 'Categorize a ticket',
        multiple: true
    })
    $('#id_groups').select2({
        multiple: true,
        width: '590px'
    })
    $('#id_user_permissions').select2({
        multiple: true,
        width: '590px',
    })
    $('#id_permissions').select2({
        multiple: true,
        width: '590px',
    })
    $('#id_resolution').select2()
    $('#id_status').select2()
}

function renderIconOption(elem) {
    let iconElement = $(elem.element).attr('icon')
    if (iconElement !== undefined)
        return $("<span class='select-option'><img class='select-option-icon' src='/" + $(elem.element).attr('icon') + "'/><p class='select-option-text'>" +  elem.text + "</p></span>")
    else
        return elem.text
}