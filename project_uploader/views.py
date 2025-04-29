from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectUploadForm
from .models import ProjectUpload

# Create your views here.

@login_required
def upload_project(request):
    if request.method == 'POST':
        form = ProjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('project_upload_success')
    else:
        form = ProjectUploadForm()
    return render(request, 'project_uploader/upload_project.html', {'form': form})

def upload_success(request):
    return render(request, 'project_uploader/success.html')

def view_projects_by_domain(request, domain_name):
    projects = ProjectUpload.objects.filter(domain=domain_name)
    return render(request, 'project_uploader/view_projects.html', {'projects': projects, 'domain': domain_name})
