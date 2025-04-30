"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from myapp.views import login_view, register_view, home_view
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('projects/', include('project_uploader.urls')),
    path('', include('myapp.urls')),
    # Password Reset URLs
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='password/password_reset.html',
             email_template_name='password/password_reset_email.html',
             subject_template_name='password/password_reset_subject.txt'
         ),
         name='password_reset'),
    
    path('password-reset/done/', 
         PasswordResetDoneView.as_view(
             template_name='password/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(
             template_name='password/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         PasswordResetCompleteView.as_view(
             template_name='password/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

