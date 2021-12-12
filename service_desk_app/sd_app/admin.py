from django.contrib import admin

# Register your models here.

from .models import Issue, Comment, Issueassocation, BookInstance

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookInstance)