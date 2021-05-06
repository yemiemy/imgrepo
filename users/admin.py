from django.contrib import admin
from .models import Profile, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
# Register your models here.
admin.site.register(Profile)