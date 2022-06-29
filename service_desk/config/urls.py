from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app import views

handler400 = 'app.views.bad_request'
handler401 = 'app.views.unauthorized'
handler403 = 'app.views.permission_denied'
handler404 = 'app.views.page_not_found'
handler405 = 'app.views.method_not_allowed'
handler500 = 'app.views.internal_server_error'
urlpatterns = [
    path('', views.TicketBoardView.as_view(), name='home'),
    path('ticket/create', views.TicketCreateView.as_view(), name='create_ticket'),
    path('ticket/filter/', views.TicketFilterView.as_view(), name='filter_ticket'),
    path('ticket/view/<slug:slug>', views.TicketDetailView.as_view(),  name='view_ticket'),
    path('ticket/clone/<slug:slug>', views.TicketCloneView.as_view(), name='clone_ticket'),
    path('ticket/edit/<slug:slug>', views.TicketEditView.as_view(), name='edit_ticket'),
    path('ticket/edit/<slug:slug>/status', views.TicketEditStatusView.as_view(), name='edit_ticket_status'),
    path('ticket/edit/<slug:slug>/assignee', views.TicketEditAssigneeView.as_view(), name='edit_ticket_assignee'),
    path('ticket/edit/<slug:slug>/suspended', views.TicketEditSuspendView.as_view(), name='edit_ticket_suspend'),
    path('ticket/edit/<slug:slug>/attachment/add', views.TicketAddAttachmentView.as_view(), name='edit_ticket_attachment_add'),
    path('ticket/edit/<slug:slug>/attachment/delete', views.TicketDeleteAttachmentView.as_view(), name='edit_ticket_attachment_delete'),
    path('ticket/edit/<slug:slug>/relation/add', views.TicketAddRelationView.as_view(), name='edit_ticket_relation_add'),
    path('ticket/edit/<slug:slug>/relation/delete', views.TicketDeleteRelationView.as_view(), name='edit_ticket_relation_delete'),
    path('ticket/edit/<slug:slug>/comment/add', views.TicketAddCommentView.as_view(), name='edit_ticket_comment_add'),
    path('ticket/edit/<slug:slug>/comment/delete', views.TicketDeleteCommentView.as_view(), name='edit_ticket_comment_delete'),
    path('ticket/edit/<slug:slug>/comment/edit', views.TicketEditCommentView.as_view(), name='edit_ticket_comment_edit'),
    path('tenant/update', views.tenant_update, name='tenant_update'),
    path('tenant/update/?P<str:tenant_check>/', views.tenant_update, name='tenant_update'),
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logged-out/', views.logged_out, name='logged_out'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/success', views.PasswordChangeSuccessView.as_view(), name='password_change_success'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/sent', views.PasswordResetSentView.as_view(), name='password_reset_sent'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/success', views.PasswordResetSuccessView.as_view(), name='password_reset_success')] \
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
