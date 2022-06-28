from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.admin import views as admin_views
from app import views
#from service_desk.app import views

handler400 = 'app.views.bad_request'
handler401 = 'app.views.unauthorized'
handler403 = 'app.views.permission_denied'
handler404 = 'app.views.page_not_found'
handler405 = 'app.views.method_not_allowed'
handler500 = 'app.views.internal_server_error'
urlpatterns = [
    #path('',
    #     views.home,
    #     name='home'),
    path('tenant/update',
         views.tenant_update,
         name='tenant_update'),
    path('tenant/update/?P<str:tenant_check>/',
         views.tenant_update,
         name='tenant_update'),
    path('login/',
         auth_views.LoginView.as_view(
             template_name='login.html',
             redirect_authenticated_user=True),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),
    path('logged-out/',
         views.logged_out,
         name='logged_out'),
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='password/password-change.html',
             success_url=reverse_lazy('password_change_success')),
         name='password_change'),
    path('password-change/success',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='password/password-change-success.html'),
         name='password_change_success'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password/password-reset.html',
             subject_template_name='password/password-reset-subject.txt',
             email_template_name='password/password-reset-email.html',
             success_url=reverse_lazy('password_reset_sent')),
         name='password_reset'),
    path('password-reset/sent',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password/password-reset-sent.html'),
         name='password_reset_sent'),
    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password/password-reset-confirm.html',
             success_url=reverse_lazy('password_reset_success')),
         name='password_reset_confirm'),
    path('password-reset/success',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password/password-reset-success.html'),
         name='password_reset_success'),
    path('ticket/create',
         views.TicketCreateView.as_view(
             template_name='ticket/ticket-create.html'),
         name='create_ticket'),
    path('ticket/view/<slug:slug>',
         views.TicketDetailView.as_view(
             template_name='ticket/ticket-view.html'),
         name='view_ticket'),
    path('ticket/clone/<slug:slug>',
         views.TicketDetailClone.as_view(),
         name='clone_ticket'),
    path('ticket/edit/<slug:slug>',
         views.TicketDetailEdit.as_view(),
         name='edit_ticket'),
    path('ticket/edit/<slug:slug>/status',
         views.TicketDetailEditStatus.as_view(),
         name='edit_ticket_status'),
    path('ticket/edit/<slug:slug>/assignee',
         views.TicketDetailEditAssignee.as_view(),
         name='edit_ticket_assignee'),
    path('ticket/edit/<slug:slug>/suspended',
         views.TicketDetailEditSuspend.as_view(),
         name='edit_ticket_suspend'),
    path('ticket/edit/<slug:slug>/attachment/add',
         views.TicketDetailAddAttachment.as_view(),
         name='edit_ticket_attachment_add'),
    path('ticket/edit/<slug:slug>/attachment/delete',
         views.TicketDetailDeleteAttachment.as_view(),
         name='edit_ticket_attachment_delete'),
    path('ticket/edit/<slug:slug>/relation/add',
         views.TicketDetailAddRelation.as_view(),
         name='edit_ticket_relation_add'),
    path('ticket/edit/<slug:slug>/relation/delete',
         views.TicketDetailDeleteRelation.as_view(),
         name='edit_ticket_relation_delete'),
    path('ticket/edit/<slug:slug>/comment/add',
         views.TicketDetailAddComment.as_view(),
         name='edit_ticket_comment_add'),
    path('ticket/edit/<slug:slug>/comment/delete',
         views.TicketDetailDeleteComment.as_view(),
         name='edit_ticket_comment_delete'),
    path('ticket/edit/<slug:slug>/comment/edit',
         views.TicketDetailEditComment.as_view(),
         name='edit_ticket_comment_edit'),
    path('ticket/filter/',
         views.TicketFilterListView.as_view(
             template_name='ticket/ticket-filter.html'),
         name='filter_ticket'),
    path('',
         views.TicketBoardListView.as_view(
             template_name='home.html'),
         name='home'),
    path('admin/',
         admin.site.urls),
    path('tinymce/',
         include('tinymce.urls'))] \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
