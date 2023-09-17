from django.db import models

class Note(models.Model):
    text = models.TextField()
    status = models.CharField(max_length=20)
    relation = models.CharField(max_length=200)
    unique_number = models.CharField(max_length=100)
