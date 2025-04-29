from django.db import models
from django.contrib.auth.models import User

class ProjectUpload(models.Model):
    DOMAIN_CHOICES = [
        ('Healthcare', 'Healthcare'),
        ('Electronics', 'Electronics'),
        ('Robotics', 'Robotics'),
        ('Data Science', 'Data Science'),
        ('Machine Learning', 'Machine Learning'),
        ('Agriculture', 'Agriculture'),
        ('Internet of Things (IoT)', 'Internet of Things (IoT)'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Augmented Reality (AR)', 'Augmented Reality (AR)'),
        ('Virtual Reality (VR)', 'Virtual Reality (VR)'),
        ('Mixed Reality (MR)', 'Mixed Reality (MR)'),
        ('Android Development', 'Android Development'),
        ('Cloud Computing', 'Cloud Computing'),
        ('MLOps', 'MLOps'),
        ('Defence', 'Defence'),
        ('Aerospace', 'Aerospace'),
        ('Building Management', 'Building Management'),
        ('Environment', 'Environment'),
        ('Artificial Intelligence (AI)', 'Artificial Intelligence (AI)'),
        ('Waste Management', 'Waste Management'),
        ('Smart Cities', 'Smart Cities'),
        ('Smart Homes', 'Smart Homes'),
        ('Automotive', 'Automotive'),
        ('Industrial Automation', 'Industrial Automation'),
        ('Energy Monitoring', 'Energy Monitoring'),
        ('Water Management', 'Water Management'),
        ('Transportation', 'Transportation'),
        ('Smart Education', 'Smart Education'),
        ('Assistive Technology', 'Assistive Technology'),
        ('Consumer Electronics', 'Consumer Electronics'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='projects/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
