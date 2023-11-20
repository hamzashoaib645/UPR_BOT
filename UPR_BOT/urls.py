"""UPR_BOT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
path('', views.Login, name='Login'),
path('doLogout/', views.doLOGOUT, name='doLogout'),
path('doLOGIN/', views.doLOGIN, name='doLOGIN'),
    path('index/', views.index, name='index'),
path('register_user/', views.register_user, name='register_user'),
path('add_user/', views.add_user, name='add_user'),
path('timetable/', views.timetable, name='timetable'),
path('Admin_home/', views.Admin_home, name='Admin_home'),
path('user_home/', views.user_home, name='user_home'),
path('add_timetable/', views.add_timetable, name='add_timetable'),
path('view_timetable/', views.view_timetable, name='view_timetable'),
path('datesheet/', views.datesheet, name='datesheet'),
path('view_datesheet/', views.view_datesheet, name='view_datesheet'),
path('add_datesheet/', views.add_datesheet, name='add_datesheet'),
path('update_profile/', views.update_profile, name='update_profile'),
path('profile_update/', views.profile_update, name='profile_update'),
path('view_user/', views.view_user, name='view_user'),
path('staff/', views.staff, name='staff'),
path('add_staff/', views.add_staff, name='add_staff'),
path('view_staff/', views.view_staff, name='view_staff'),
path('delete_user/<str:id>', views.delete_user, name='delete_user'),
path('delete_timetable/<str:id>', views.delete_timetable, name='delete_timetable'),
path('delete_datesheet/<str:id>', views.delete_datesheet, name='delete_datesheet'),
path('delete_staff/<str:id>', views.delete_staff, name='delete_staff'),
path('view_history/', views.view_history, name='view_history'),
path('delete_history/<str:id>', views.delete_history, name='delete_history'),
path('admin_view_history/', views.admin_view_history, name='admin_view_history'),
path('admin_reply/', views.admin_reply, name='admin_reply'),
path('admin_responses/', views.admin_responses, name='admin_responses'),
path('bot_responses/', views.bot_responses, name='bot_responses'),
path('add_bot_responses/', views.add_bot_responses, name='add_bot_responses'),
path('train_model/', views.train_model, name='train_model'),
]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
