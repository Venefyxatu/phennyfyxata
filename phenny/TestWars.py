import time
import json
import requests
import nanowars
import commands
import datetime

from unittest import TestCase
from nanowars import WarTooLongError


class HelperFunctions:

    def call_django(self, location, method='GET', urldata=None):
        method = method in ['GET', 'POST'] and method or 'GET'
        url = 'http://localhost:8000%s' % location
        if method == 'GET':
            result = requests.get(url)
        elif method == 'POST':
            result = requests.post(url, urldata)

        return result


class DummyPhenny:
    def __init__(self, expected_start=None, expected_end=None):
        self.said = []
        self.expected_start = expected_start
        self.expected_end = expected_end
        self.expected_score = None
        self.expected_war_id = None
        self.expected_nick = None

    def say(self, what):
        self.said.append(what)
        if 'STOP' in what:
            assert datetime.datetime.now().strftime('%H:%M') == self.expected_end.strftime('%H:%M'), 'Expected STOP at %s, not %s' % (self.expected_end, datetime.datetime.now())
        elif 'START' in what:
            assert datetime.datetime.now().strftime('%H:%m') == self.expected_start.strftime('%H:%m'), 'Expected START at %s, not %s' % (self.expected_start, datetime.datetime.now())

        elif what == '3':
            assert datetime.datetime.now().strftime('%H:%m') == (self.expected_start - datetime.timedelta(seconds=3)).strftime('%H:%m')
        elif what == '2':
            assert datetime.datetime.now().strftime('%H:%m') == (self.expected_start - datetime.timedelta(seconds=2)).strftime('%H:%m')
        elif what == '1':
            assert datetime.datetime.now().strftime('%H:%m') == (self.expected_start - datetime.timedelta(seconds=1)).strftime('%H:%m')


class DummyInput:
    def __init__(self, nick=None):
        self.properties = [None]
        self.nick = nick if nick else 'Testie'

    def group(self, index):
        return self.properties[index]


class ParticipateTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.start = self.now + datetime.timedelta(minutes=1) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        self.end = self.now + datetime.timedelta(minutes=2) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')

    def test_invalid_data(self):
        phenny = DummyPhenny()

        nick = 'Testie'

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('999')

        nanowars.participate(phenny, inputobj)

        assert 'Die war ken ik niet, %s' % nick in phenny.said, 'Phenny should warn that she doesn\'t know an unplanned war.'

    def test_participate(self):
        nick = 'Testie'
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)

        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick in phenny.said, 'Phenny should confirm participation.'

        time_to_wait = int(self.end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        expected_said = '%s, war 1 begint over 10 seconden.' % nick
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))
        phenny_said = filter(lambda said: 'STOP' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people when stopping the war, instead she said: %s' % '\n'.join(phenny.said)
        assert nick in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))

    def test_participate_again(self):
        nick = 'Testie'
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)
        nanowars.participate(phenny, inputobj)

        assert 'Geen zorgen %s, ik was nog niet vergeten dat je meedoet :-)' % nick in phenny.said, 'Phenny should say that %s already participates' % nick

        time_to_wait = int(self.end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        expected_said = '%s, war 1 begint over 10 seconden.' % nick
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))
        phenny_said = filter(lambda said: 'STOP' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people when stopping the war, instead she said: %s' % '\n'.join(phenny.said)
        assert nick in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))

    def test_two_participants(self):
        nick = 'Testie'
        nick2 = 'AnotherTester'
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)
        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick in phenny.said, 'Phenny should confirm participation.'

        inputobj = DummyInput(nick2)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)

        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick2 in phenny.said, 'Phenny should confirm participation.'

        time_to_wait = int(self.end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        phenny_said = filter(lambda said: 'war 1 begint over 10 seconden' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people, instead she said: %s' % '\n'.join(phenny.said)
        assert nick in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))
        assert nick2 in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick2, '\n'.join(phenny.said))
        phenny_said = filter(lambda said: 'STOP' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people when stopping the war, instead she said: %s' % '\n'.join(phenny.said)
        assert nick in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))
        assert nick2 in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick2, '\n'.join(phenny.said))

    def test_withdraw(self):
        nick = 'Testie'
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)

        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick in phenny.said, 'Phenny should confirm participation.'

        inputobj = DummyInput(nick)
        inputobj.properties.append('withdraw')
        inputobj.properties.append('1')

        nanowars.withdraw(phenny, inputobj)

        assert 'OK, ik schrap je uit de deelnemerslijst, %s.' % nick, 'Phenny should confirm that %s doesn\'t participate' % nick

        time_to_wait = int(self.end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        expected_said = '%s, war 1 begint over 10 seconden.' % nick
        assert expected_said not in phenny.said, 'Expected phenny not to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))
        phenny_said = filter(lambda said: 'STOP' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should stopped the war, instead she said: %s' % '\n'.join(phenny.said)
        assert nick not in phenny_said[0], 'Phenny should not have notified %s when stopping the war, instead she said: %s' % '\n'.join(phenny.said)

    def test_withdraw_not_participating(self):
        nick = 'Testie'
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('withdraw')
        inputobj.properties.append('1')

        nanowars.withdraw(phenny, inputobj)

        assert 'Je deed niet mee, %s :-)' % nick in phenny.said, 'Phenny should tell %s that he wasn\'t participating.'

    def test_one_of_two_withdraws(self):
        nick = 'Testie'
        nick2 = 'AnotherTester'
        start = self.start + datetime.timedelta(minutes=1)
        end = self.end + datetime.timedelta(minutes=1)
        phenny = DummyPhenny(start, end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (start.strftime('%H:%M'), end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        inputobj = DummyInput(nick)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)
        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick in phenny.said, 'Phenny should confirm participation.'

        inputobj = DummyInput(nick2)
        inputobj.properties.append('participate')
        inputobj.properties.append('1')

        nanowars.participate(phenny, inputobj)

        assert 'OK, ik verwittig je persoonlijk 10 seconden voordat war 1 begint, en nog eens wanneer de war eindigt, %s' % nick2 in phenny.said, 'Phenny should confirm participation.'

        inputobj = DummyInput(nick)
        inputobj.properties.append('withdraw')
        inputobj.properties.append('1')

        nanowars.withdraw(phenny, inputobj)

        assert 'OK, ik schrap je uit de deelnemerslijst, %s.' % nick, 'Phenny should confirm that %s doesn\'t participate' % nick

        time_to_wait = int(end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        phenny_said = filter(lambda said: 'war 1 begint over 10 seconden' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people, instead she said: %s' % '\n'.join(phenny.said)
        assert nick not in phenny_said[0], 'Phenny should not have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))
        assert nick2 in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick2, '\n'.join(phenny.said))
        phenny_said = filter(lambda said: 'STOP' in said, phenny.said)
        assert len(phenny_said) == 1, 'Phenny should have notified people when stopping the war, instead she said: %s' % '\n'.join(phenny.said)
        assert nick not in phenny_said[0], 'Phenny should not have notified %s when stopping the war, instead she said: %s' % (nick, '\n'.join(phenny.said))
        assert nick2 in phenny_said[0], 'Phenny should have notified %s when stopping the war, instead she said: %s' % (nick2, '\n'.join(phenny.said))


class WarTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.start = self.now + datetime.timedelta(minutes=1) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        self.end = self.now + datetime.timedelta(minutes=2) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')

    def test_not_enough_arguments(self):
        nick = 'Testie'
        phenny = DummyPhenny()
        inputobj = DummyInput()

        inputobj.properties.append('war')
        inputobj.properties.append(self.start.strftime('%H:%M'))

        nanowars.war(phenny, inputobj)

        expected_said = 'Ik moet wel weten wanneer de war start EN eindigt, %s. Als ik hem alleen moet stoppen moet je busy zeggen als startuur.' % nick

        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

    def test_busy_war(self):
        end = self.now + datetime.timedelta(minutes=1)
        end -= datetime.timedelta(seconds=end.second, microseconds=end.microsecond)
        phenny = DummyPhenny()
        phenny.expected_end = end
        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('busy %s' % end.strftime('%H:%M'))
        inputobj.properties.append(end)

        nanowars.war(phenny, inputobj)

        time.sleep(2)

        expected_said = 'Ik zal het stopsein geven om %s.' % end.strftime('%H:%M')
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))
        expected_unsaid = 'Ik zal het startsein geven om %s.' % self.now.strftime('%H:%M')
        assert expected_unsaid not in phenny.said, 'Expected phenny not to say %s, instead she said %s' % (expected_unsaid, '\n'.join(phenny.said))

        time_to_wait = int(end.strftime('%s')) - time.time()

        time.sleep(time_to_wait + 5)

        assert len(filter(lambda x: 'War 1: STOP' in x, phenny.said)) > 0, 'phenny.say was not called with STOP'

    def test_war(self):
        phenny = DummyPhenny(self.start, self.end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)
        time_to_wait = int(self.end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)
        duration = (self.end - self.start).seconds / 60
        assert 'START war 1 (van %s tot %s, %s %s dus)' % (self.start.strftime('%H:%M'),
                self.end.strftime('%H:%M'),
                duration,
                'minuut' if duration == 1 else 'minuten') in phenny.said, 'phenny.say was not called with START'
        assert len(filter(lambda x: 'War 1: STOP' in x, phenny.said)) > 0, 'phenny.say was not called with STOP'
        assert '3' in phenny.said, 'phenny.say was not called with 3'
        assert '2' in phenny.said, 'phenny.say was not called with 2'
        assert '1' in phenny.said, 'phenny.say was not called with 1'
        assert 'War 1 is voorbij. Je kan je score registreren met .score 1 <score>' in phenny.said, 'phenny did not say how to register score'
        assert 'Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/1/overview/' in phenny.said, 'phenny did not say where to find the score list'

    def test_war_too_long(self):
        end = self.now + datetime.timedelta(hours=6) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)

        phenny = DummyPhenny(self.start, end)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), end.strftime('%H:%M')))
        nanowars.war(phenny, inputobj)

        expected_said = 'Een war van meer dan 5 uur? Ik dacht het niet.'
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

    def test_two_wars_last_planned_first(self):
        phenny = DummyPhenny(self.start, self.end)

        phenny2 = DummyPhenny(self.start + datetime.timedelta(minutes=2), self.end + datetime.timedelta(minutes=2))

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))

        inputobj2 = DummyInput()
        inputobj2.properties.append('war')
        inputobj2.properties.append('%s %s' % (phenny2.expected_start.strftime('%H:%M'), phenny2.expected_end.strftime('%H:%M')))

        nanowars.war(phenny2, inputobj2)
        nanowars.war(phenny, inputobj)

        time_to_wait = int(phenny2.expected_end.strftime('%s')) - time.time()
        time.sleep(time_to_wait + 5)

        duration = (self.end - self.start).seconds / 60
        assert 'START war 2 (van %s tot %s, %s %s dus)' % (self.start.strftime('%H:%M'),
                self.end.strftime('%H:%M'),
                duration,
                'minuut' if duration == 1 else 'minuten') in phenny.said, 'phenny.say was not called with START'
        assert len(filter(lambda x: 'War 2: STOP' in x, phenny.said)) > 0, 'phenny.say was not called with STOP'
        assert '3' in phenny.said, 'phenny.say was not called with 3'
        assert '2' in phenny.said, 'phenny.say was not called with 2'
        assert '1' in phenny.said, 'phenny.say was not called with 1'
        assert 'War 2 is voorbij. Je kan je score registreren met .score 2 <score>' in phenny.said, 'phenny did not say how to register score'
        assert 'Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/2/overview/' in phenny.said, 'phenny did not say where to find the score list'

        duration = (phenny2.expected_end - phenny2.expected_start).seconds / 60
        assert 'START war 1 (van %s tot %s, %s %s dus)' % (phenny2.expected_start.strftime('%H:%M'),
                phenny2.expected_end.strftime('%H:%M'),
                duration,
                'minuut' if duration == 1 else 'minuten') in phenny2.said, 'phenny2.say was not called with START'
        assert len(filter(lambda x: 'War 1: STOP' in x, phenny2.said)) > 0, 'phenny2.say was not called with STOP'
        assert '3' in phenny2.said, 'phenny2.say was not called with 3'
        assert '2' in phenny2.said, 'phenny2.say was not called with 2'
        assert '1' in phenny2.said, 'phenny2.say was not called with 1'
        assert 'War 1 is voorbij. Je kan je score registreren met .score 1 <score>' in phenny2.said, 'phenny2 did not say how to register score'
        assert 'Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/1/overview/' in phenny2.said, 'phenny2 did not say where to find the score list'

    def test_schedule_war(self):

        war_data = nanowars._schedule_war(start=self.start.strftime('%s'), end=self.end.strftime('%s'))
        expected_data = {'id': 1, 'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')}
        assert war_data == expected_data, 'War data should be %s, not %s' % (expected_data, war_data)

        result = HelperFunctions().call_django('/api/war/planned/')
        planned_wars = json.loads(result.content)

        expected_response = [{'id': 1, 'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')}]

        assert planned_wars == expected_response, 'Planned wars is %s, not %s' % (planned_wars, expected_response)


class ScoreTest(TestCase):
    def setUp(self):
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')
        self.start = datetime.datetime.now() - datetime.timedelta(minutes=10)
        self.end = datetime.datetime.now() - datetime.timedelta(minutes=5)

        self.nick = 'testie'

    def test_register_score(self):
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')})
        self.war = json.loads(result.content)

        phenny = DummyPhenny()

        phenny.expected_score = 200
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])

        nanowars.score(phenny, inputobj)

        result = HelperFunctions().call_django('/api/writer/getscore/', 'POST', {'writer': self.nick, 'war': self.war['id']})
        scoredata = json.loads(result.content)

        expected_response = {'writer': self.nick, 'war': str(self.war['id']), 'score': 200}

        assert scoredata == expected_response, 'Response should be %s, not %s' % (expected_response, scoredata)

        expected_say = 'Score %s staat genoteerd voor war %s, %s.' % (phenny.expected_score, phenny.expected_war_id, phenny.expected_nick)
        assert expected_say in phenny.said, 'Expected %s in phenny.said, instead she said: %s' % (expected_say, '\n'.join(phenny.said))

    def test_register_score_nonexisting_war(self):
        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('999 200')
        nanowars.score(phenny, inputobj)

        assert 'Die war ken ik niet, %s' % self.nick in phenny.said

    def test_invalid_data(self):
        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('abc def')

        nanowars.score(phenny, inputobj)

        assert 'Ik heb twee getalletjes nodig, %s: het nummer van de war gevolgd door je score' % self.nick in phenny.said, 'Phenny did not say what was wrong, instead she said: %s' % '\n'.join(phenny.said)

    def test_score_old_war(self):
        start = datetime.datetime.now() - datetime.timedelta(days=1, minutes=10)
        end = datetime.datetime.now() - datetime.timedelta(days=1, minutes=5)
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')})
        self.war = json.loads(result.content)

        phenny = DummyPhenny()

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])

        nanowars.score(phenny, inputobj)

        expected_said = 'Die war is een dag of meer geleden gestopt. Als je heel zeker bent dat je er nog een score voor wil registreren, zeg dan .score %s %s zeker' % (self.war['id'], 200)
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

        result = HelperFunctions().call_django('/api/writer/getscore/', 'POST', {'writer': self.nick, 'war': self.war['id']})
        scoredata = json.loads(result.content)

        assert scoredata == {}, 'Phenny should not have registered score, but got %s from backend.' % scoredata

    def test_score_old_war_certain(self):
        start = datetime.datetime.now() - datetime.timedelta(days=1, minutes=10)
        end = datetime.datetime.now() - datetime.timedelta(days=1, minutes=5)
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')})
        self.war = json.loads(result.content)

        phenny = DummyPhenny()
        phenny.expected_score = 200
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200 zeker' % self.war['id'])

        nanowars.score(phenny, inputobj)

        expected_say = 'Score %s staat genoteerd voor war %s, %s.' % (phenny.expected_score, phenny.expected_war_id, phenny.expected_nick)
        assert expected_say in phenny.said, 'Expected %s in phenny.said, instead she said: %s' % (expected_say, '\n'.join(phenny.said))

    def test_unregister_score(self):
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')})
        self.war = json.loads(result.content)

        phenny = DummyPhenny()
        phenny.expected_score = 200
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])
        nanowars.score(phenny, inputobj)

        result = HelperFunctions().call_django('/api/writer/getscore/', 'POST', {'writer': self.nick, 'war': self.war['id']})
        scoredata = json.loads(result.content)

        expected_response = {'writer': self.nick, 'war': str(self.war['id']), 'score': 200}

        assert scoredata == expected_response, 'Response should be %s, not %s' % (expected_response, scoredata)

        expected_say = 'Score %s staat genoteerd voor war %s, %s.' % (phenny.expected_score, phenny.expected_war_id, phenny.expected_nick)
        assert expected_say in phenny.said

        phenny = DummyPhenny()
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 0' % self.war['id'])
        nanowars.score(phenny, inputobj)

        expected_said = 'Ik heb je score voor war %s verwijderd, %s.' % (self.war['id'], self.nick)

        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))


class InfoTest(TestCase):
    def setUp(self):
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')
        self.nick = 'Testie'

    def test_no_planned_wars(self):
        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('plannedwars')

        nanowars.plannedwars(phenny, inputobj)

        expected_said = 'Er zijn geen wars gepland.'

        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

    def test_planned_wars(self):
        start = datetime.datetime.now() + datetime.timedelta(minutes=5)
        end = datetime.datetime.now() + datetime.timedelta(minutes=10)
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')})
        wardata = json.loads(result.content)

        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('plannedwars')

        nanowars.plannedwars(phenny, inputobj)

        starttime = int(wardata['starttime'])
        endtime = int(wardata['endtime'])
        delta = (endtime - starttime) / 60
        expected_said = ['Deze wars zijn nog gepland:',
                'War %s: van %s tot %s (%s minuten dus)' % (wardata['id'], datetime.datetime.fromtimestamp(starttime).strftime('%H:%M'),
                    datetime.datetime.fromtimestamp(endtime).strftime('%H:%M'), delta)]

        for expected in expected_said:
            assert expected in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected, '\n'.join(phenny.said))

    def test_no_active_wars(self):
        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('activewars')

        nanowars.activewars(phenny, inputobj)

        expected_said = 'Er zijn geen wars bezig.'

        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

    def test_active_wars(self):
        start = datetime.datetime.now() - datetime.timedelta(minutes=5)
        end = datetime.datetime.now() + datetime.timedelta(minutes=10)
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')})
        wardata = json.loads(result.content)

        phenny = DummyPhenny()
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('plannedwars')

        nanowars.activewars(phenny, inputobj)

        starttime = int(wardata['starttime'])
        endtime = int(wardata['endtime'])
        delta = (endtime - starttime) / 60
        expected_said = ['Deze wars zijn bezig:',
                'War %s: van %s tot %s (%s minuten dus)' % (wardata['id'], datetime.datetime.fromtimestamp(starttime).strftime('%H:%M'),
                    datetime.datetime.fromtimestamp(endtime).strftime('%H:%M'), delta)]

        for expected in expected_said:
            assert expected in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected, '\n'.join(phenny.said))


class TimeTest(TestCase):
    def shortDescription(self):
        ''' Hack to prevent docstring from being used with nosetests -v
        see http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/
        '''

        return None

    def setUp(self):
        self.now = datetime.datetime.now()
        self.planning_hour = datetime.datetime(self.now.year, self.now.month, self.now.day, 15)

    def test_start_before_end_before_lt_max(self):
        start = self.planning_hour - datetime.timedelta(hours=1)
        end = self.planning_hour - datetime.timedelta(minutes=30)

        result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)

        expected_start = (start + datetime.timedelta(days=1)).strftime('%s')
        expected_end = (end + datetime.timedelta(days=1)).strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_start_before_end_past_lt_max(self):
        start = self.planning_hour - datetime.timedelta(minutes=30)
        end = self.planning_hour + datetime.timedelta(minutes=30)

        result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)

        expected_start = (start + datetime.timedelta(days=1)).strftime('%s')
        expected_end = (end + datetime.timedelta(days=1)).strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_start_past_end_past_lt_max(self):
        start = self.planning_hour + datetime.timedelta(hours=1)
        end = self.planning_hour + datetime.timedelta(hours=1, minutes=30)

        result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)

        expected_start = start.strftime('%s')
        expected_end = end.strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_start_before_end_before_gt_max(self):
        start = self.planning_hour - datetime.timedelta(hours=6)
        end = self.planning_hour - datetime.timedelta(minutes=30)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_before_end_past_gt_max(self):
        start = self.planning_hour - datetime.timedelta(hours=4)
        end = self.planning_hour + datetime.timedelta(hours=1, minutes=30)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_past_end_past_gt_max(self):
        start = self.planning_hour + datetime.timedelta(hours=1)
        end = self.planning_hour + datetime.timedelta(hours=6, minutes=30)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_before_end_before_lt_max_wrong_order(self):
        start = self.planning_hour - datetime.timedelta(hours=5)
        end = self.planning_hour - datetime.timedelta(hours=6)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
            assert e.message == 'Het beginuur moet wel voor het einduur liggen he!', 'Got wrong message (%s) for war with end hour before starting hour.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_before_end_before_gt_max_wrong_order(self):
        start = self.planning_hour - datetime.timedelta(hours=5)
        end = self.planning_hour - datetime.timedelta(hours=11)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
            assert e.message == 'Het beginuur moet wel voor het einduur liggen he!', 'Got wrong message (%s) for war with end hour before starting hour.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_past_end_past_lt_max_wrong_order(self):
        start = self.planning_hour + datetime.timedelta(hours=2)
        end = self.planning_hour + datetime.timedelta(hours=1)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_past_end_past_gt_max_wrong_order(self):
        start = self.planning_hour + datetime.timedelta(hours=2)
        end = self.planning_hour + datetime.timedelta(hours=1)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_busy_end_past_lt_max(self):
        start = 'busy'
        end = self.planning_hour + datetime.timedelta(hours=1)

        result_start, result_end = nanowars._convert_to_epoch(start, end.strftime('%H:%M'), self.planning_hour)

        expected_start = self.planning_hour.strftime('%s')
        expected_end = end.strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_busy_end_past_gt_max(self):
        start = 'busy'
        end = self.planning_hour + datetime.timedelta(hours=6)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start, end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_busy_end_before(self):
        start = 'busy'
        end = self.planning_hour - datetime.timedelta(hours=1)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start, end.strftime('%H:%M'), self.planning_hour)
        except WarTooLongError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_today_past_end_tomorrow_past_lt_max(self):
        start = datetime.datetime(self.now.year, self.now.month, self.now.day, 23, 30)
        end = datetime.datetime(self.now.year, self.now.month, self.now.day, 0, 30)
        planning_hour = datetime.datetime(self.now.year, self.now.month, self.now.day, 0, 20)

        result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), planning_hour)

        expected_start = start.strftime('%s')
        expected_end = (end + datetime.timedelta(days=1)).strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_start_today_past_end_tomorrow_before_lt_max(self):
        '"before" in this context means that the hour has already passed on the CURRENT day'

        start = datetime.datetime(self.now.year, self.now.month, self.now.day, 23, 30)
        end = datetime.datetime(self.now.year, self.now.month, self.now.day, 0, 30)
        planning_hour = datetime.datetime(self.now.year, self.now.month, self.now.day, 23, 00)

        result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), planning_hour)

        expected_start = start.strftime('%s')
        expected_end = (end + datetime.timedelta(days=1)).strftime('%s')

        assert result_start == expected_start, 'Expected start: %s (%s). Received start: %s (%s)' % (expected_start, datetime.datetime.fromtimestamp(int(expected_start)), result_start, datetime.datetime.fromtimestamp(int(result_start)))
        assert result_end == expected_end, 'Expected end: %s (%s). Received end: %s (%s)' % (expected_end, datetime.datetime.fromtimestamp(int(expected_end)), result_end, datetime.datetime.fromtimestamp(int(result_end)))

    def test_start_today_before_end_tomorrow_before_lt_max(self):

        start = datetime.datetime(self.now.year, self.now.month, self.now.day, 23, 30)
        end = datetime.datetime(self.now.year, self.now.month, self.now.day, 0, 30)
        planning_hour = datetime.datetime(self.now.year, self.now.month, self.now.day, 23, 40)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), planning_hour)
        except RuntimeError, e:
            assert e.message == 'Het beginuur moet wel voor het einduur liggen he!', 'Got wrong message (%s) for war with end hour before starting hour.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'
