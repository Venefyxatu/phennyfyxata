import json
import datetime

from django.test import TestCase
from django.test.client import Client

from scores.models import War
from scores.models import Writer
from scores.models import WarParticipants
from scores.models import ParticipantScore


class ParticipationHelper:
    def participate(self, war_id, writer_nick):
        response = Client().post('/api/war/participate/', {'id': war_id, 'writer': writer_nick})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

    def withdraw(self, war_id, writer_nick):
        response = Client().post('/api/war/withdraw/', {'id': war_id, 'writer': writer_nick})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code


class ParticipantTests(TestCase):
    def setUp(self):
        starttime = datetime.datetime.now() + datetime.timedelta(0, seconds=300)
        endtime = starttime + datetime.timedelta(0, seconds=600)

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
        response = self.c.post('/api/war/participate/', {'id': 9, 'writer': self.writer.nick})
        assert response.status_code == 404, 'Response status should be 404, not %s' % response.status_code

    def test_list_participants(self):
        self.ph.participate(self.war.id, self.writer.nick)

        participants = WarParticipants.objects.filter(war__id=self.war.id)
        assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        response = self.c.post('/api/war/listparticipants/', {'id': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = [self.writer.nick]
        assert json.loads(response.content) == expected_response, 'Response should be "%s", not %s' % (expected_response, json.loads(response.content))

        self.ph.participate(self.war.id, 'NewWriter')

        participants = WarParticipants.objects.filter(war__id=self.war.id)
        assert len(participants) == 2, 'Should have 1 participant, not %s' % len(participants)

        response = self.c.post('/api/war/listparticipants/', {'id': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = [self.writer.nick, 'NewWriter']
        assert json.loads(response.content) == expected_response, 'Response should be "%s", not %s' % (expected_response, json.loads(response.content))

        self.ph.withdraw(self.war.id, self.writer.nick)

        participants = WarParticipants.objects.filter(war__id=self.war.id)
        assert len(participants) == 1, 'Should have 1 participant, not %s' % len(participants)

        response = self.c.post('/api/war/listparticipants/', {'id': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = ['NewWriter']
        assert json.loads(response.content) == expected_response, 'Response should be "%s", not %s' % (expected_response, json.loads(response.content))

        self.ph.withdraw(self.war.id, 'NewWriter')

        participants = WarParticipants.objects.filter(war__id=self.war.id)
        assert len(participants) == 0, 'Should have 0 participants, not %s' % len(participants)

        response = self.c.post('/api/war/listparticipants/', {'id': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        assert json.loads(response.content) == [], 'Response should be [], not %s' % json.loads(response.content)


class WarTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.starttime = datetime.datetime.now() + datetime.timedelta(0, seconds=300)
        self.starttime = self.starttime - datetime.timedelta(0, seconds=self.starttime.second, microseconds=self.starttime.microsecond)
        self.endtime = self.starttime + datetime.timedelta(0, seconds=600)
        self.endtime = self.endtime - datetime.timedelta(0, seconds=self.endtime.second, microseconds=self.endtime.microsecond)

    def test_war_info(self):
        response = self.c.post('/api/war/new/', {'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        response = self.c.post('/api/war/info/', {'id': 1})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        expected_response = {'id': '1', 'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')}

        assert json.loads(response.content) == expected_response, 'Response should be %s, not %s' % (expected_response, json.loads(response.content))

    def test_create_war(self):
        response = self.c.post('/api/war/new/', {'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        assert len(War.objects.all()) == 1, 'There should be 1 war, not %s' % len(War.objects.all())

    def test_no_active_wars(self):
        response = self.c.post('/api/war/new/', {'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        response = self.c.get('/api/war/active/')
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        assert json.loads(response.content) == [], 'Response should be [], not %s' % json.loads(response.content)

    def test_active_wars(self):
        starttime = datetime.datetime.now()
        starttime = starttime - datetime.timedelta(0, seconds=starttime.second, microseconds=starttime.microsecond)
        response = self.c.post('/api/war/new/', {'starttime': starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        response = self.c.get('/api/war/active/')
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = [{'id': 1, 'starttime': starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')}]
        assert json.loads(response.content) == expected_response, 'Response should be "%s", not %s' % (expected_response, json.loads(response.content))

    def test_planned_wars(self):
        response = self.c.post('/api/war/new/', {'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        response = self.c.get('/api/war/planned/')
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = [{'id': 1, 'starttime': self.starttime.strftime('%s'), 'endtime': self.endtime.strftime('%s')}]
        assert json.loads(response.content) == expected_response, 'Response should be %s, not %s' % (expected_response, json.loads(response.content))

    def test_no_planned_wars(self):
        response = self.c.get('/api/war/planned/')
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        expected_response = []
        assert json.loads(response.content) == expected_response, 'Response should be %s, not %s' % (expected_response, json.loads(response.content))


class ScoreTests(TestCase):
    def setUp(self):
        starttime = datetime.datetime.now() + datetime.timedelta(0, seconds=300)
        endtime = starttime + datetime.timedelta(0, seconds=600)

        self.war = War(starttime=starttime, endtime=endtime)
        self.war.save()
        self.writer = Writer(nick='TestWriter')
        self.writer.save()
        self.c = Client()

    def test_get_score_for_war(self):
        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 200, 'war': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        response = self.c.post('/api/writer/getscore/', {'writer': self.writer.nick, 'war': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        expected_response = {'war': str(self.war.id), 'writer': self.writer.nick, 'score': 200}

        assert json.loads(response.content) == expected_response, 'Response should be %s, not %s' % (expected_response, json.loads(response.content))

    def test_register_score(self):
        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 200, 'war': self.war.id})

        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        assert len(ParticipantScore.objects.all()) == 1, 'There should be one ParticipantScore object'

        ps = ParticipantScore.objects.all()[0]

        assert ps.writer == self.writer, 'ParticipantScore writer is not as expected'
        assert ps.score == 200, 'ParticipantScore score should be 200, not %s' % ps.score
        assert ps.war == self.war, 'ParticipantScore war is not as expected'

    def test_deregister_score(self):
        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 200, 'war': self.war.id})

        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        assert len(ParticipantScore.objects.all()) == 1, 'There should be one ParticipantScore object'

        ps = ParticipantScore.objects.all()[0]

        assert ps.writer == self.writer, 'ParticipantScore writer is not as expected'
        assert ps.score == 200, 'ParticipantScore score should be 200, not %s' % ps.score
        assert ps.war == self.war, 'ParticipantScore war is not as expected'

        response = self.c.post('/api/score/deregister/', {'writer': self.writer.nick, 'war': self.war.id})

        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        assert len(ParticipantScore.objects.all()) == 0, 'There should be no ParticipantScore objects'

    def test_update_score(self):
        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 200, 'war': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code
        assert len(ParticipantScore.objects.all()) == 1, 'There should be one ParticipantScore object'

        ps = ParticipantScore.objects.all()[0]
        assert ps.score == 200, 'ParticipantScore score should be 200, not %s' % ps.score

        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 400, 'war': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        ps = ParticipantScore.objects.all()[0]
        assert ps.score == 400, 'ParticipantScore score should be 400, not %s' % ps.score

        response = self.c.post('/api/score/register/', {'writer': self.writer.nick, 'score': 100, 'war': self.war.id})
        assert response.status_code == 200, 'Response status should be 200, not %s' % response.status_code

        ps = ParticipantScore.objects.all()[0]
        assert ps.score == 100, 'ParticipantScore score should be 100, not %s' % ps.score
