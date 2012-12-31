from django.db import models


class Writer(models.Model):
    alias = models.ForeignKey('Writer', blank=True, null=True)
    nick = models.CharField(unique=True, max_length=16)


class War(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    finished = models.BooleanField(default=False)

    def __unicode__(self):
        return "War %s: %s tot %s (%s minuten)" % (self.id, self.starttime.strftime("%H:%M"), self.endtime.strftime("%H:%M"), (self.endtime - self.starttime).seconds / 60)


class ParticipantScore(models.Model):
    writer = models.ForeignKey(Writer)
    war = models.ForeignKey(War)
    score = models.IntegerField(default=0, blank=True)


class WriterStats(models.Model):
    warcount = models.IntegerField()
    wordcount = models.IntegerField()
    wpm = models.DecimalField(max_digits=5, decimal_places=2)


class WarParticipants(models.Model):
    war = models.ForeignKey(War)
    participant = models.ForeignKey(Writer)
