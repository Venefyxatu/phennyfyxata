#!/usr/bin/env python
# coding=utf-8

import json
import urllib
import urllib2
import datetime
from threading import Timer

#djangoUrl = 'http://phenny.venefyxatu.be/'
djangoUrl = 'http://localhost:8000/'
action = chr(1) + 'ACTION '


def _schedule_war(start, end):
    result = _call_django('api/war/new/', 'POST', {'starttime': start, 'endtime': end})

    lines = '\n'.join(result.readlines())
    return json.loads(lines)


def _convert_to_epoch(start, end, planning_hour):
    if start == 'busy':
        start = planning_hour
        start -= datetime.timedelta(seconds=start.second, microseconds=start.microsecond)
    else:
        start = datetime.datetime.strptime('%s %s %s %s' % (planning_hour.year, planning_hour.month, planning_hour.day, start), '%Y %m %d %H:%M')

    end = datetime.datetime.strptime('%s %s %s %s' % (planning_hour.year, planning_hour.month, planning_hour.day, end), '%Y %m %d %H:%M')

    start, end = _check_and_add_day(start, end, planning_hour)

    if abs(end - start) > datetime.timedelta(hours=5):
        raise RuntimeError('Een war van meer dan 5 uur? Ik dacht het niet.')

    return start.strftime('%s'), end.strftime('%s')


def _check_and_add_day(start, end, planning_hour):
    if start < planning_hour:
        start += datetime.timedelta(days=1)

    if end < planning_hour:
        end += datetime.timedelta(days=1)

    if end < start:
        if end.day == planning_hour.day:
            end += datetime.timedelta(days=1)
        else:
            raise RuntimeError('Het beginuur moet wel voor het einduur liggen he!')
    return start, end


def _call_django(location, method='GET', urldata=None):
    method = method in ['GET', 'POST'] and method or 'GET'
    url = djangoUrl + location

    if urldata:
        urldata = urllib.urlencode(urldata)

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=urldata)
    request.add_header('Content-Type', 'text/http')
    request.get_method = lambda: method
    result = opener.open(request)
    return result


def war(phenny, input):
    """
    Time een war
    """
    planning_hour = datetime.datetime.now()
    args = input.group(2)
    start, end = args.split()
    start, end = _convert_to_epoch(start, end, planning_hour)
    result = _schedule_war(start, end)
    wait = int(int(result['starttime']) - int(datetime.datetime.now().strftime('%s')))
    t = Timer(wait, phenny.say, ['START war %s' % result['id']])
    t.start()
    wait_end = int(int(result['endtime']) - int(datetime.datetime.now().strftime('%s')))
    t_end = Timer(wait_end, phenny.say, ['END war %s' % result['id']])
    t_end.start()


war.commands = ['war']
war.example = '.war 15:50 16:00'


def warsoverview(phenny, input):
    """ Geef een overzicht van de actieve wars
    """
    result = _call_django('wars/%s' % input[1:-4])
    wars = result.read()
    if not wars:
        if input == '.plannedwars':
            phenny.say('Er zijn geen wars gepland')
        else:
            phenny.say('Er zijn geen wars bezig')
    wars = wars.split(',')
    for war in wars:
        phenny.say(war)

warsoverview.commands = ['activewars', 'plannedwars']


def score(phenny, input):
    """
    Registreer je score
    """

    params = input.group(2).split(' ')
    try:
        war_id = int(params[0])
        score = int(params[1])
    except ValueError:
        phenny.say("Ik heb twee getalletjes nodig, %s: het nummer van de war gevolgd door je score" % input.nick)
        return
    confirm = False
    if len(params) == 3 and params[2].lower() == 'zeker':
        confirm = True
    try:
        result = _call_django('wars/%s/info/' % war_id, 'GET')
    except urllib2.HTTPError:
        phenny.say('Die war ken ik niet, %s' % input.nick)
        return
    war_info = result.read()
    war_info = eval(war_info)
    war_end_delta = datetime.datetime.now() - datetime.datetime.strptime(war_info['end'], '%Y-%m-%d %H:%M:%S')
    if war_end_delta.days >= 1 and not confirm:
        phenny.say('Die war is een dag of meer geleden gestopt. Als je heel zeker bent dat je er nog een score voor wil registreren, zeg dan .score %s %s zeker' % (war_id, score))
        return
    result = _call_django('writers/%s/registerscore/' % input.nick, 'POST', {'score': score, 'war': war_id})
    if result.msg == 'OK':
        if score == 0:
            phenny.say('Ik heb je score voor war %s verwijderd, %s.' % (war_id, input.nick))
        else:
            phenny.say('Score %s staat genoteerd voor war %s, %s.' % (score, war_id, input.nick))

score.commands = ['score']
score.example = '.score 1 2003'

if __name__ == '__main__':
    print __doc__.strip()
