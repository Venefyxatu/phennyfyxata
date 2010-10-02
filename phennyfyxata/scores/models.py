from django.db import models

class Writer(models.Model):
    nick = models.CharField(unique=True, max_length=16)

class War(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    endtime = models.DateTimeField()
    finished = models.BooleanField(default=False)

class ParticipantScore(models.Model):
    writer = models.ForeignKey(Writer)
    war = models.ForeignKey(War)
    score = models.IntegerField(default=0, blank=True)
