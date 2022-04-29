# config URL Configuration
#   The `urlpatterns` list routes URLs to views. For more information please see:
#       https://docs.djangoproject.com/en/3.2/topics/http/urls/
#   Examples:
#       Function views
#           1. Add an import:  from my_app import views
#           2. Add a URL to urlpatterns:  path('', views.home, name='home')
#       Class-based views
#           1. Add an import:  from other_app.views import Home
#           2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
#       Including another URLconf
#           1. Import the include() function: from django.urls import include, path
#           2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app import views

handler400 = 'app.views.bad_request'
handler403 = 'app.views.permission_denied'
handler404 = 'app.views.page_not_found'
handler500 = 'app.views.internal_server_error'

urlpatterns = [path('', views.home, name='home'),
               # path('accounts/', include('django.contrib.auth.urls')),
               path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
               path('logout/', auth_views.LogoutView.as_view(), name='logout'),
               path('logged-out/', views.logged_out, name='logged_out'),
               path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password-change.html'), name='password_change'),
               path('admin/', admin.site.urls),
               path('test/', views.test, name='test')]
               # path('login/', views.login, name='login'),
