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
    def say(self, say_what):
        return say_what


class WarTest(TestCase):
    def setUp(self):
        self.phenny = DummyPhenny()
        self.now = datetime.datetime.now()
        commands.getstatusoutput('python /home/erik/source/phennyfyxata/phennyfyxata/manage.py flush --noinput')

    def test_schedule_war(self):
        start = self.now + datetime.timedelta(minutes=5) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)
        end = self.now + datetime.timedelta(minutes=9) - datetime.timedelta(microseconds=self.now.microsecond) - datetime.timedelta(seconds=self.now.second)

        war_data = nanowars._schedule_war(self.phenny, start=start.strftime('%H:%M'), end=end.strftime('%H:%M'), planning_hour=self.now)
        expected_data = {'id': 1, 'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')}
        assert war_data == expected_data, 'War data should be %s, not %s' % (expected_data, war_data)

        result = HelperFunctions().call_django('/api/war/planned/')
        lines = '\n'.join(result.readlines())
        planned_wars = json.loads(lines)

        expected_response = [{'id': 1, 'starttime': start.strftime('%s'), 'endtime': end.strftime('%s')}]

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