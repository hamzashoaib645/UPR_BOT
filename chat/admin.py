from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Define how you want the admin page for CustomUser to look
    list_display = ('username','user_type')
    list_filter = ('user_type',)

admin.site.register(CustomUser, CustomUserAdmin)
# Register your models here.
class UserModel(UserAdmin):
    List_display = ['username', 'user_type']

admin.site.register(Timetable)
admin.site.register(Datesheet)
admin.site.register(Staff)
admin.site.register(ChatHistory)