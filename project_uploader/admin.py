from django.contrib import admin
from .models import ProjectUpload

@admin.register(ProjectUpload)
class ProjectUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'domain', 'uploaded_at')
    list_filter = ('domain', 'uploaded_at', 'user')
    search_fields = ('title', 'description', 'user__username')
