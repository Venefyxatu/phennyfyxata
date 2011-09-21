#!/usr/bin/env python
# coding=utf-8

import re
import time
import urllib
import urllib2
import datetime

from modules.scheduler import RunOnce
from modules.scheduler import Scheduler
from modules.scheduler import every_x_mins
from modules.scheduler import every_x_secs

djangoUrl = 'http://phenny.venefyxatu.be/'
scheduler = Scheduler()
action = chr(1)+'ACTION '

_TIME_REGEX = re.compile('[0-2]?[0-9]:[0-5]?[0-9]')
_WARID_REGEX = re.compile('War (\d+):')
_WARSTART_REGEX = re.compile('War \d+: (\d{1,2}:\d{1,2}) tot')
_WAREND_REGEX = re.compile('tot (\d{1,2}:\d{1,2})')

def setup(phenny):
    scheduler.start()
    #_check_planned_wars(phenny)

def _to_epoch(hour, minute):
    now = datetime.datetime.now()
    war = datetime.datetime(now.year, now.month, now.day, hour, minute)
    if war.hour < now.hour:
        war = war + datetime.timedelta(days=1)
    elif war.hour == now.hour and war.minute < now.minute:
        war = war + datetime.timedelta(days=1)
    return war

def _check_planned_wars(phenny):
    # Will also be called on reload - doesn't need to happen then
    result = _call_django('wars/planned')
    for war in result.read().split(','):
        war_data = _extract_war_data(war)
        _schedule_war(phenny, war_data)

def _extract_war_data(war):
    match = re.search(_WARID_REGEX, war)
    id = int(match.groups()[0])
    match = re.search(_WARSTART_REGEX, war)
    start = match.groups()[0]
    start_hour, start_minute = start.split(':')
    match = re.search(_WAREND_REGEX, war)
    end = match.groups()[0]
    end_hour, end_minute = start.split(':')
    return {'id': id, 'start_hour': int(start_hour), 'start_minute': int(start_minute), 'end_hour': int(end_hour), 'end_minute': int(end_minute)}

def _schedule_war(phenny, war_data):
    starttime = _to_epoch(war_data['start_hour'], war_data['start_minute'])
    endtime = _to_epoch(war_data['end_hour'], war_data['end_minute'])
    if 'id' not in war_data.keys():
        urldata = {
                "starttime": starttime.strftime('%s'),
                "endtime": endtime.strftime('%s')}
        war_data['id'] = _call_django('wars/new/', 'POST', urldata=urldata).read()
    if hasattr(phenny, 'say'):
        phenny.say('War %s gepland van %s:%s tot %s:%s.' % (war_data['id'], war_data['start_hour'], war_data['start_minute'], war_data['end_hour'], war_data['end_minute']))
    start_receipt = scheduler.schedule('War %s start' % war_data['id'], starttime, every_x_secs(10), RunOnce(start_war, {'phenny': phenny, 'war_id': war_data['id']}))
    print 'scheduling end'
    end_receipt = scheduler.schedule('War %s end' % war_data['id'], endtime, every_x_secs(10), RunOnce(stop_war, {'phenny': phenny, 'war_id': war_data['id']}))

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

def _parse_arguments(arguments):
    start, end = arguments.split()
    if start.lower() == 'busy':
        start = time.strftime('%H:%M', time.localtime())
    try:
        starttuple = time.strptime(start, '%H:%M')
        endtuple = time.strptime(end, '%H:%M')
        start_hour, start_minute = starttuple.tm_hour, starttuple.tm_min
        end_hour, end_minute = endtuple.tm_hour, endtuple.tm_min
    except:
        raise RuntimeError('Oei, dat is een uur dat niet op mijn horloge staat :(')
    return int(start_hour), int(start_minute), int(end_hour), int(end_minute)

def start_war(phenny, war_id):
    phenny.say('War %s start NU!' % war_id)

def stop_war(phenny, war_id):
    phenny.say('War %s stopt NU!' % war_id)

def war(phenny, input): 
    """
    Time een war
    """
    
    try:
        start_hour, start_minute, end_hour, end_minute = _parse_arguments(input.group(2))
    except RuntimeError, e:
        phenny.say(e.message)
        return
    _schedule_war(phenny, {'start_hour': start_hour, 'start_minute': start_minute, 'end_hour': end_hour, 'end_minute': end_minute})

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
    result = _call_django('writers/%s/registerscore/' % input.nick, 'POST', {'score': score, 'war': war_id})
    if result.msg == 'OK':
        phenny.say("Score %s staat genoteerd voor war %s, %s." % (score, war_id, input.nick))

score.commands = ['score']
score.example = '.score 1 2003'

if __name__ == '__main__': 
    print __doc__.strip()
