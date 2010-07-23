from django.db import models

# Create your models here.

class Writer(models.Model):
    nick = models.CharField(unique=True, max_length=16)
    totalscore = models.IntegerField(default=0)
    totalwars = models.IntegerField(default=0)
