import time
import json
import urllib
import urllib2
import nanowars
import commands
import datetime

from unittest import TestCase


class HelperFunctions:

    def call_django(self, location, method='GET', urldata=None):
        method = method in ['GET', 'POST'] and method or 'GET'
        url = 'http://localhost:8000%s' % location

        if urldata:
            urldata = urllib.urlencode(urldata)

        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=urldata)
        request.add_header('Content-Type', 'text/http')
        request.get_method = lambda: method
        result = opener.open(request)
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


class DummyInput:
    def __init__(self, nick=None):
        self.properties = [None]
        self.nick = nick if nick else 'Testie'

    def group(self, index):
        return self.properties[index]


class WarTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.start = self.now + datetime.timedelta(minutes=1) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        self.end = self.now + datetime.timedelta(minutes=2) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')

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
        assert len(filter(lambda x: x.startswith('War 1: STOP'), phenny.said)) > 0, 'phenny.say was not called with STOP'
        assert '3' in phenny.said, 'phenny.say was not called with 3'
        assert '2' in phenny.said, 'phenny.say was not called with 2'
        assert '1' in phenny.said, 'phenny.say was not called with 1'
        assert 'War 1 is voorbij. Je kan je score registreren met .score 1 <score>' in phenny.said, 'phenny did not say how to register score'
        assert 'Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/1/overview/' in phenny.said, 'phenny did not say where to find the score list'

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
        assert len(filter(lambda x: x.startswith('War 2: STOP'), phenny.said)) > 0, 'phenny.say was not called with STOP'
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
        assert len(filter(lambda x: x.startswith('War 1: STOP'), phenny2.said)) > 0, 'phenny2.say was not called with STOP'
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
        lines = '\n'.join(result.readlines())
        planned_wars = json.loads(lines)

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
        lines = '\n'.join(result.readlines())

        self.war = json.loads(lines)

        phenny = DummyPhenny()

        phenny.expected_score = 200
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick
        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])

        nanowars.score(phenny, inputobj)

        result = HelperFunctions().call_django('/api/writer/getscore/', 'POST', {'writer': self.nick, 'war': self.war['id']})

        lines = '\n'.join(result.readlines())

        scoredata = json.loads(lines)

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
        lines = '\n'.join(result.readlines())

        self.war = json.loads(lines)

        phenny = DummyPhenny()

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])

        nanowars.score(phenny, inputobj)

        expected_said = 'Die war is een dag of meer geleden gestopt. Als je heel zeker bent dat je er nog een score voor wil registreren, zeg dan .score %s %s zeker' % (self.war['id'], 200)
        assert expected_said in phenny.said, 'Expected phenny to say %s, instead she said %s' % (expected_said, '\n'.join(phenny.said))

    def test_score_old_war_certain(self):
        start = datetime.datetime.now() - datetime.timedelta(days=1, minutes=10)
        end = datetime.datetime.now() - datetime.timedelta(days=1, minutes=5)
        result = HelperFunctions().call_django('/api/war/new/', 'POST', {'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')})
        lines = '\n'.join(result.readlines())

        self.war = json.loads(lines)

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
        lines = '\n'.join(result.readlines())

        self.war = json.loads(lines)

        phenny = DummyPhenny()
        phenny.expected_score = 200
        phenny.expected_war_id = self.war['id']
        phenny.expected_nick = self.nick

        inputobj = DummyInput(self.nick)
        inputobj.properties.append('score')
        inputobj.properties.append('%s 200' % self.war['id'])
        nanowars.score(phenny, inputobj)

        result = HelperFunctions().call_django('/api/writer/getscore/', 'POST', {'writer': self.nick, 'war': self.war['id']})

        lines = '\n'.join(result.readlines())

        scoredata = json.loads(lines)

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
        lines = '\n'.join(result.readlines())
        wardata = json.loads(lines)

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
        lines = '\n'.join(result.readlines())
        wardata = json.loads(lines)

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
        except RuntimeError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_before_end_past_gt_max(self):
        start = self.planning_hour - datetime.timedelta(hours=4)
        end = self.planning_hour + datetime.timedelta(hours=1, minutes=30)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_past_end_past_gt_max(self):
        start = self.planning_hour + datetime.timedelta(hours=1)
        end = self.planning_hour + datetime.timedelta(hours=6, minutes=30)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
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
        except RuntimeError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_start_past_end_past_gt_max_wrong_order(self):
        start = self.planning_hour + datetime.timedelta(hours=2)
        end = self.planning_hour + datetime.timedelta(hours=1)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start.strftime('%H:%M'), end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
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
        except RuntimeError, e:
            assert e.message == 'Een war van meer dan 5 uur? Ik dacht het niet.', 'Got wrong message (%s) for war longer than 5 hours.' % e.message
            raised = True

        assert raised == True, 'Expected an error to be raised'

    def test_busy_end_before(self):
        start = 'busy'
        end = self.planning_hour - datetime.timedelta(hours=1)

        raised = False

        try:
            result_start, result_end = nanowars._convert_to_epoch(start, end.strftime('%H:%M'), self.planning_hour)
        except RuntimeError, e:
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
