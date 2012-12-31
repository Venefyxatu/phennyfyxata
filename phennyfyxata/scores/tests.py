import datetime

from django.test import TestCase
from django.test.client import Client

from scores.models import War
from scores.models import Writer
from scores.models import WarParticipants


class ParticipantTests(TestCase):
        def setUp(self):
            starttime = datetime.datetime.now() + datetime.timedelta(0, 300)
            endtime = starttime + datetime.timedelta(0, 600)

            self.war = War(starttime=starttime, endtime=endtime)
            self.war.save()
            self.writer = Writer(nick='TestWriter')
            self.writer.save()
            self.c = Client()

        def test_participate_war(self):
            response = self.c.post('/wars/%s/participate/' % self.war.id, {'writer': self.writer.nick})
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

            participants = WarParticipants.objects.filter(war__id=self.war.id, participant__id=self.writer.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        def test_withdraw_war(self):
            response = self.c.post('/wars/%s/participate/' % self.war.id, {'writer': self.writer.nick})
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

            participants = WarParticipants.objects.filter(war__id=self.war.id, participant__id=self.writer.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

            response = self.c.post('/wars/%s/withdraw/' % self.war.id, {'writer': self.writer.nick})
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

            participants = WarParticipants.objects.filter(war__id=self.war.id, participant__id=self.writer.id)
            assert len(participants) == 0, 'Should have 0 participants, not %s' % len(participants)
