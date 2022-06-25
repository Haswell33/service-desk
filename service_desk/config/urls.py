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
handler500 = 'app.views.internal_server_error'
urlpatterns = [
    #path('',
    #     views.home,
    #     name='home'),
    path('tenant/update',
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
    #path('ticket/submit',
    #     views.submit_ticket,
    #     name='submit_ticket'),
    path('ticket/view/<slug:slug>',
         views.TicketDetailView.as_view(
             template_name='ticket/ticket-view.html'),
         name='view_ticket'),
    path('ticket/update/<slug:slug>',
         views.TicketDetailUpdate.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket'),
    path('ticket/update/status/<slug:slug>',
         views.TicketDetailUpdateStatus.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_status'),
    path('ticket/update/assignee/<slug:slug>',
         views.TicketDetailUpdateAssignee.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_assignee'),
    path('ticket/update/suspended/<slug:slug>',
         views.TicketDetailUpdateSuspend.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_suspend'),
    path('ticket/update/attachment/add/<slug:slug>/',
         views.TicketDetailAddAttachment.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_attachment_add'),
    path('ticket/update/attachment/delete/<slug:slug>/',
         views.TicketDetailDeleteAttachment.as_view(
            template_name='ticket/ticket-view.html'),
         name='update_ticket_attachment_delete'),
    path('ticket/update/relation/add/<slug:slug>/',
         views.TicketDetailAddRelation.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_relation_add'),
    path('ticket/update/relation/delete/<slug:slug>/',
         views.TicketDetailDeleteRelation.as_view(
             template_name='ticket/ticket-view.html'),
         name='update_ticket_relation_delete'),
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
