from django.contrib import admin
from django.urls import path, include
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
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password-change.html'), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password-reset.html'), name='password_reset'),
    path('logged-out/', views.logged_out, name='logged_out'),
    path('admin/', admin.site.urls),
    path('ticket/create', views.create_ticket, name='create_ticket'),
    path('ticket/submit', views.submit_ticket, name='submit_ticket')] \
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
