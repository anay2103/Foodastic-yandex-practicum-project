from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, MyUser


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
        'is_active')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
