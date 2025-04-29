from django import forms
from .models import ProjectUpload

class ProjectUploadForm(forms.ModelForm):
    class Meta:
        model = ProjectUpload
        fields = ['domain', 'title', 'description', 'file'] 