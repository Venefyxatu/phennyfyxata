import datetime

from django.test import TestCase
from django.test.client import Client

from scores.models import War
from scores.models import Writer
from scores.models import WarParticipants


class ParticipationHelper:
    def participate(self, war_id, writer_nick):
        response = Client().post('/wars/%s/participate/' % war_id, {'writer': writer_nick})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

    def withdraw(self, war_id, writer_nick):
        response = Client().post('/wars/%s/withdraw/' % war_id, {'writer': writer_nick})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code


class ParticipantTests(TestCase):
        def setUp(self):
            starttime = datetime.datetime.now() + datetime.timedelta(0, 300)
            endtime = starttime + datetime.timedelta(0, 600)

            self.ph = ParticipationHelper()

            self.war = War(starttime=starttime, endtime=endtime)
            self.war.save()
            self.writer = Writer(nick='TestWriter')
            self.writer.save()
            self.c = Client()

        def test_participate_war(self):
            self.ph.participate(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        def test_withdraw_war(self):
            self.ph.participate(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

            self.ph.withdraw(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 0, 'Should have 0 participants, not %s' % len(participants)

        def test_add_new_participant(self):
            self.ph.participate(self.war.id, 'NewWriter')

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        def test_add_same_participant(self):
            self.ph.participate(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

            self.ph.participate(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        def test_withdraw_unparticipating_writer(self):
            self.ph.withdraw(self.war.id, 'NewWriter')

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 0, 'Should have 0 participants, not %s' % len(participants)

        def test_participate_nonexistant_war(self):
            response = self.c.post('/wars/%s/participate/' % 9, {'writer': self.writer.nick})
            assert response.status_code == 404, 'Response status should be 404, not %s' % response.status_code

        def test_list_participants(self):
            self.ph.participate(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

            response = self.c.get('/wars/%s/listparticipants/' % self.war.id)
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
            assert response.content == self.writer.nick, 'Response should be "%s", not %s' % (self.writer.nick, response.content)

            self.ph.participate(self.war.id, 'NewWriter')

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 2, 'Should have 1 participant, not %s' % len(participants)

            response = self.c.get('/wars/%s/listparticipants/' % self.war.id)
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
            expected_response = ','.join([self.writer.nick, 'NewWriter'])
            assert response.content == expected_response, 'Response should be "%s", not %s' % (expected_response, response.content)

            self.ph.withdraw(self.war.id, self.writer.nick)

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

            response = self.c.get('/wars/%s/listparticipants/' % self.war.id)
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
            assert response.content == 'NewWriter', 'Response should be "NewWriter", not %s' % response.content

            self.ph.withdraw(self.war.id, 'NewWriter')

            participants = WarParticipants.objects.filter(war__id=self.war.id)
            assert len(participants) == 0, 'Should have 0 participants, not %s' % len(participants)

            response = self.c.get('/wars/%s/listparticipants/' % self.war.id)
            assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
            assert response.content == '', 'Response should be empty string, not %s' % response.content
