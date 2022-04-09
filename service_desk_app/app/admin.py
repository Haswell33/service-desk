from django.contrib import admin

# Register your models here.

from service_desk_app.app.models import BookInstance

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookInstance)