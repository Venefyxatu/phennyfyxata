import time
import json
import types
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


class assertMethodIsCalled(object):
    def __init__(self, obj, method):
        self.obj = obj
        self.method = method

    def called(self, *args, **kwargs):
        self.method_called = True
        self.orig_method(*args, **kwargs)

    def __enter__(self):
        self.orig_method = getattr(self.obj, self.method)
        setattr(self.obj, self.method, self.called)
        self.method_called = False

    def __exit__(self, exc_type, exc_value, traceback):
        expected_start = int(self.obj.expected_start.strftime('%s'))
        now = int(datetime.datetime.now().strftime('%s'))
        if  expected_start > now:
            time.sleep(expected_start - now + 5)

        assert getattr(self.obj, self.method) == self.called, "method %s was modified during assertMethodIsCalled" % self.method

        setattr(self.obj, self.method, self.orig_method)

        # If an exception was thrown within the block, we've already failed.
        if traceback is None:
            assert self.method_called, "method %s of %s was not called" % (self.method, self.obj)


class DummyPhenny:
    def say(self, say_what):
        return say_what


class DummyInput:
    properties = [None]

    def group(self, index):
        return self.properties[index]


class WarTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.start = self.now + datetime.timedelta(minutes=2) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        self.end = self.now + datetime.timedelta(minutes=3) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')

    def test_war(self):
        phenny = DummyPhenny()
        phenny.expected_start = self.start
        phenny.expected_end = self.end

        def say(self, what):
            print what
            if 'START' in what:
                assert self.expected_start.strftime('%H:%M') == datetime.datetime.now().strftime('%H:%M')
            elif 'END' in what:
                assert self.expected_end.strftime('%H:%M') == datetime.datetime.now().strftime('%H:%M')
            else:
                assert True == False, 'Expected START or END in %s' % what

        phenny.say = types.MethodType(say, phenny)

        inputobj = DummyInput()
        inputobj.properties.append('war')
        inputobj.properties.append('%s %s' % (self.start.strftime('%H:%M'), self.end.strftime('%H:%M')))
        with assertMethodIsCalled(phenny, 'say'):
            nanowars.war(phenny, inputobj)

    def test_schedule_war(self):

        war_data = nanowars._schedule_war(start=self.start.strftime('%s'), end=self.end.strftime('%s'))
        expected_data = {'id': 1, 'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')}
        assert war_data == expected_data, 'War data should be %s, not %s' % (expected_data, war_data)

        result = HelperFunctions().call_django('/api/war/planned/')
        lines = '\n'.join(result.readlines())
        planned_wars = json.loads(lines)

        expected_response = [{'id': 1, 'starttime': self.start.strftime('%s'), 'endtime': self.end.strftime('%s')}]

        assert planned_wars == expected_response, 'Planned wars is %s, not %s' % (planned_wars, expected_response)


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
