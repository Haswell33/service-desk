function renderFields(page, mediaUrl) {
    switch(page) {
        case 'admin':
            adminFields(mediaUrl)
            break
        case 'create-ticket':
            createTicketFields(mediaUrl)
            break
        case 'home':
            homeFields(mediaUrl)
            break
        default:
            console.error('not found provided page, can not load select2 fields')
    }
}

function adminFields(mediaUrl) {
    renderField('#id_type', mediaUrl, 'Select an issue type', true, false, false, -1)
    renderField('#id_priority', mediaUrl, 'Select a priority', true, false, false, -1)
    renderField('#id_assignee', mediaUrl, 'Select a assignee', true, true, false, 0)
    renderField('#id_reporter', mediaUrl, 'Select a reporter', true, false, false, 0)
    renderField('#id_status', mediaUrl, 'Select a status', false, false, false, -1)
    renderField('#id_resolution', mediaUrl, 'Select a resolution', false, true, false, -1)

    renderField('#id_src_status', mediaUrl, 'Select a source status', false, false, false, -1)
    renderField('#id_dest_status', mediaUrl, 'Select a destination status', false, false, false, -1)

    renderField('#id_issue_type', mediaUrl, 'Select an issue type', true, false, false, -1)
    renderField('#id_transition', mediaUrl, 'Select a destination status', false, false, false, -1)

    renderField('#id_sla', mediaUrl, 'Select a destination status', false, false, false, -1)
    renderField('#id_customers_group', mediaUrl, 'Select a customers group', false, true, false, 0)
    renderField('#id_operators_group', mediaUrl, 'Select a developers group', false, true, false, 0)
    renderField('#id_developers_group', mediaUrl, 'Select a operators group', false, true, false, 0)
    renderField('#id_customers_board', mediaUrl, 'Select a default board for customers', false, true, false, 0)
    renderField('#id_operators_board', mediaUrl, 'Select a default board for operators', false, true, false, 0)
    renderField('#id_developers_board', mediaUrl, 'Select a default board for developers', false, true, false, 0)

    renderField('#id_env_type', mediaUrl, 'Select a purpose of this object', false, true, false, -1)
    renderField('#id_board', mediaUrl, 'Select a assigned board', false, false, false, 0)
    renderField('#id_column', mediaUrl, 'Select a column where status will be displayed', false, false, false, 0)

    renderField('select[name=action]', mediaUrl, 'Select a bulk action for selected rows', false, true, false, -1)

    renderField('#id_user_permissions', mediaUrl, 'Select an user permissions', false, true, true, 0)
    renderField('#id_groups', mediaUrl, 'Select an groups', false, true, true, 0)
}

function createTicketFields(mediaUrl) {
    renderField('#id_type', mediaUrl, 'Select an issue type', true, false, false, -1)
    renderField('#id_priority', mediaUrl, 'Select a priority', true, false, false, -1)
    renderField('#id_assignee', mediaUrl, 'Select an assignee', true, true, false, 0)
    renderField('#id_labels', mediaUrl, 'Categorize a ticket', false, true, true, 0)
}

function homeFields(mediaUrl) {
    renderField('#sidebar-block_tenant-set', mediaUrl, '', true, false, false, -1)
    renderField('#filter-assignee', mediaUrl, 'Filter by assignee', true, false, false, 0)
    renderField('#filter-reporter', mediaUrl, 'Filter by reporter', true, false, false, 0)

    renderField('#filter-order-by', mediaUrl, 'Order by', false, false, false, 0)
}

function renderField(htmlTag, mediaUrl, placeholderText, icon, allowClear, multiple, minResults) {
    $(htmlTag).select2({
        templateResult: function (option)  {
            if (icon)
                return renderIconOption(option, mediaUrl)
            else
                return option.text
        },
        templateSelection: function (option)  {
            if (icon)
                return renderIconOption(option, mediaUrl)
            else
                return option.text
        },
        placeholder: placeholderText,
        allowClear: allowClear,
        multiple: multiple,
        minimumResultsForSearch: minResults
    })
}


function renderIconOption(elem, mediaUrl) {
    let iconElement = $(elem.element).attr('icon')
    if (iconElement !== undefined)
        return $("<span class='select-option'><img class='select-option-icon' src='" + mediaUrl + $(elem.element).attr('icon') + "'/><p class='select-option-text'>" +  elem.text + "</p></span>")
    else
        return elem.text
}

$(document).on('select2:select', function (event) {
    if (event.target.id === 'sidebar-block_tenant-set') {
        $.ajax({
            type: 'POST',
            url: '/tenant/update',
            data: {'tenant_id': event.params.data.id},
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
            },
            success: function(result){
                location.reload()
                console.log('active tenant changed')
            }
        })
    }
});