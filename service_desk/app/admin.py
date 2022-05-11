from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group

#from django.contrib.sites.models import Site
from app.models import Issue, Tenant, Comment

# admin.site.unregister(Site)
admin.site.register(Issue)
admin.site.register(Tenant)
admin.site.site_title = 'nowy title'
admin.site.site_header = 'nowy header'
# admin.site.unregister(Group)