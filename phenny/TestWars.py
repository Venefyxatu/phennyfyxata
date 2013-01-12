import nanowars
import datetime

from unittest import TestCase


class TimeTest(TestCase):
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
        ''' "before" in this context means that the hour has already passed on the CURRENT day '''

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
