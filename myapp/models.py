from django.db import models


class Creator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    number = models.IntegerField()

