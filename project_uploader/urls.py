from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_project, name='upload_project'),
    path('success/', views.upload_success, name='project_upload_success'),
    path('domain/<str:domain_name>/', views.view_projects_by_domain, name='view_projects_by_domain'),
] 