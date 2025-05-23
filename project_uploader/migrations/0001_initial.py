# Generated by Django 4.2.20 on 2025-04-29 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(choices=[('Healthcare', 'Healthcare'), ('Electronics', 'Electronics'), ('Robotics', 'Robotics'), ('Data Science', 'Data Science'), ('Machine Learning', 'Machine Learning'), ('Agriculture', 'Agriculture'), ('Internet of Things (IoT)', 'Internet of Things (IoT)'), ('Cybersecurity', 'Cybersecurity'), ('Augmented Reality (AR)', 'Augmented Reality (AR)'), ('Virtual Reality (VR)', 'Virtual Reality (VR)'), ('Mixed Reality (MR)', 'Mixed Reality (MR)'), ('Android Development', 'Android Development'), ('Cloud Computing', 'Cloud Computing'), ('MLOps', 'MLOps'), ('Defence', 'Defence'), ('Aerospace', 'Aerospace'), ('Building Management', 'Building Management'), ('Environment', 'Environment'), ('Artificial Intelligence (AI)', 'Artificial Intelligence (AI)'), ('Waste Management', 'Waste Management'), ('Smart Cities', 'Smart Cities'), ('Smart Homes', 'Smart Homes'), ('Automotive', 'Automotive'), ('Industrial Automation', 'Industrial Automation'), ('Energy Monitoring', 'Energy Monitoring'), ('Water Management', 'Water Management'), ('Transportation', 'Transportation'), ('Smart Education', 'Smart Education'), ('Assistive Technology', 'Assistive Technology'), ('Consumer Electronics', 'Consumer Electronics')], max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('file', models.FileField(upload_to='projects/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
