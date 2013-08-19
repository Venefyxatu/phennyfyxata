#!/usr/bin/env python
# coding=utf-8

import re
import json
import random
import requests
import datetime
from threading import Timer

djangoUrl = 'http://phenny.venefyxatu.be/'
action = chr(1) + 'ACTION '

STOPQUOTES = ['Hammertime!',
              'Hamertijd!',
              'In the name of love!',
              'In the name of fluffy little bunnies!',
              'Drop! Roll!']

CONTESTS = ['Het wereldkampioenschap zakkenvullen?',
            'Een wedstrijdje uit de maat dansen?',
            'De Olympische spelen?',
            'Een cursus onderwatermandjesvlechten voor gevorderden?']

STARTSTOP_REGEX = re.compile('(?P<start>(busy|\d{1,2}:\d{1,2})) (?P<end>\d{1,2}:\d{1,2})')
WARID_REGEX = re.compile('(war )?(?P<war_id>\d+)')


class WarTooLongError(Exception):
    pass


def _schedule_war(start, end):
    result = _call_django('api/war/new/', 'POST', {'starttime': start, 'endtime': end})

    return result


def _convert_to_epoch(start, end, planning_hour):
    if start == 'busy':
        start = planning_hour
        start -= datetime.timedelta(seconds=start.second, microseconds=start.microsecond)
    else:
        start = datetime.datetime.strptime('%s %s %s %s' % (planning_hour.year, planning_hour.month, planning_hour.day, start), '%Y %m %d %H:%M')

    end = datetime.datetime.strptime('%s %s %s %s' % (planning_hour.year, planning_hour.month, planning_hour.day, end), '%Y %m %d %H:%M')

    start, end = _check_and_add_day(start, end, planning_hour)

    if abs(end - start) > datetime.timedelta(hours=5):
        raise WarTooLongError('Een war van meer dan 5 uur? Ik dacht het niet.')

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
    if method == 'GET':
        result = requests.get(url)
    elif method == 'POST':
        result = requests.post(url, urldata)

    if result.status_code == 404:
        return None
    else:
        try:
            return json.loads(result.content)
        except ValueError:
            return result.content


def _get_war_info(path):
    result = _call_django(path, 'GET')
    return result


def _say_war_info(phenny, plannedwars):
    for plannedwar in plannedwars:
        start = datetime.datetime.fromtimestamp(int(plannedwar['starttime']))
        end = datetime.datetime.fromtimestamp(int(plannedwar['endtime']))
        delta = (end - start).seconds / 60
        phenny.say('War %s: van %s tot %s (%s minuten dus)' % (plannedwar['id'], start.strftime('%H:%M'), end.strftime('%H:%M'), delta))


def war(phenny, input):
    """
    Time een war
    """
    planning_hour = datetime.datetime.now()
    planning_hour -= datetime.timedelta(seconds=planning_hour.second, microseconds=planning_hour.microsecond)
    args = input.group(2)
    match = re.match(STARTSTOP_REGEX, args)
    if not match:
        phenny.say('Ik moet wel weten wanneer de war start EN eindigt, %s. Als ik hem alleen moet stoppen moet je busy zeggen als startuur.' % input.nick)
        return
    else:
        groupdict = match.groupdict()
        start = groupdict['start']
        end = groupdict['end']

    try:
        start, end = _convert_to_epoch(start, end, planning_hour)
    except WarTooLongError, e:
        phenny.say(e.message)
        return
    result = _schedule_war(start, end)

    start_dt = datetime.datetime.fromtimestamp(int(start))
    end_dt = datetime.datetime.fromtimestamp(int(end))
    start_human = start_dt.strftime('%H:%M')
    end_human = end_dt.strftime('%H:%M')
    duration_human = (end_dt - start_dt).seconds / 60
    if planning_hour != start_dt:
        phenny.say('Ik zal het startsein geven voor war %s om %s.' % (result['id'], start_human))
        wait = int(int(result['starttime']) - int(datetime.datetime.now().strftime('%s')))

        for x in xrange(3, 0, -1):
            t = Timer(wait - x, phenny.say, [str(x)])
            t.start()

        t_notify = Timer(wait - 10, warn_participants_start, [phenny, result['id']])
        t_notify.start()

        t = Timer(wait,
                phenny.say, ['START war %s (van %s tot %s, %s %s dus)' % (result['id'],
                                                                start_human,
                                                                end_human,
                                                                duration_human,
                                                                'minuut' if duration_human == 1 else 'minuten')])
        t.start()
    phenny.say('Ik zal het stopsein geven om %s.' % end_human)
    wait_end = int(int(result['endtime']) - int(datetime.datetime.now().strftime('%s')))
    t_end = Timer(wait_end, stop_war, [phenny, result['id']])
    t_end.start()
    t_score = Timer(wait_end + 2, phenny.say, ['War %s is voorbij. Je kan je score registreren met .score %s <score>' % (result['id'], result['id'])])
    t_score.start()
    t_deelnemers = Timer(wait_end + 3, phenny.say, ['Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/%s/overview/' % result['id']])
    t_deelnemers.start()


war.commands = ['war']
war.example = '.war 15:50 16:00'


def stop_war(phenny, war_id):
    participants = _call_django('api/war/listparticipants/', 'POST', {'id': war_id})

    participantstring = ', '.join(participants) if participants else ''

    phenny.say('%s War %s: STOP - %s' % (participantstring, war_id, random.choice(STOPQUOTES)))


def warn_participants_start(phenny, war_id):
    participants = _call_django('api/war/listparticipants/', 'POST', {'id': war_id})

    if participants:
        participants = ', '.join(participants)
        chunks = [participants[x:x+10] for x in xrange(0, len(participants), 10)]
        for chunk in chunks:
            phenny.say('%s, war %s begint over 10 seconden.' % (chunk, war_id))


def plannedwars(phenny, input):
    ''' Geef een overzicht van de geplande wars '''
    plannedwars = _get_war_info('api/war/planned/')
    if plannedwars:
        phenny.say('Deze wars zijn nog gepland:')
        _say_war_info(phenny, plannedwars)
    else:
        phenny.say('Er zijn geen wars gepland.')

plannedwars.commands = ['plannedwars']


def activewars(phenny, input):
    ''' Geef een overzicht van de actieve wars '''
    activewars = _get_war_info('api/war/active/')
    if activewars:
        phenny.say('Deze wars zijn bezig:')
        _say_war_info(phenny, activewars)
    else:
        phenny.say('Er zijn geen wars bezig.')

activewars.commands = ['activewars']


def score(phenny, input):
    writer_nick = input.nick
    values = input.group(2).split()
    try:
        war_id = int(values[0])
        score = int(values[1])
        sure = True if len(values) == 3 and values[2] == 'zeker' else False
    except (ValueError, IndexError):
        phenny.say('Ik heb twee getalletjes nodig, %s: het nummer van de war gevolgd door je score' % writer_nick)
        return

    war_info = _call_django('api/war/info/', 'POST', {'id': war_id})

    if not war_info:
        phenny.say("Volgens de annalen bestaat war %s niet. Ik verlies geen documenten, dus ik vermoed dat je je vergist met het ID :-) " % war_id)
        return
    elif (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(war_info['endtime']))).days >= 1 and not sure:
        phenny.say('Die war is een dag of meer geleden gestopt. Als je heel zeker bent dat je er nog een score voor wil registreren, zeg dan .score %s %s zeker' % (war_id, score))
        return

    if score == 0:
        result = _call_django('api/score/deregister/', 'POST', {'writer': writer_nick, 'war': war_id})
    else:
        result = _call_django('api/score/register/', 'POST', {'writer': writer_nick, 'score': score, 'war': war_id})

    if result == 'OK' and score == 0:
        phenny.say('Ik heb je score voor war %s verwijderd, %s.' % (war_id, writer_nick))
    elif result == 'OK':
        phenny.say('Score %s staat genoteerd voor war %s, %s.' % (score, war_id, writer_nick))

score.commands = ['score']
score.example = '.score 1 2003'


def _get_warid(phenny, args, writer_nick):

    match = re.match(WARID_REGEX, args).groupdict()

    if not 'war_id' in match:
        phenny.say('Oei, ik begrijp niet welke war je bedoelt, %s' % writer_nick)
        return None

    return match['war_id']


def withdraw(phenny, input):
    writer_nick = input.nick
    args = input.group(2)
    if not args:
        phenny.say('Ja, maar waaraan wil je niet meer deelnemen, %s? %s' % (writer_nick, random.choice(CONTESTS)))
        return

    war_id = _get_warid(phenny, args, writer_nick)

    if not war_id:
        return

    participants = _call_django('api/war/listparticipants/', 'POST', {'id': war_id})

    if writer_nick not in participants:
        phenny.say('Je deed niet mee, %s :-)' % writer_nick)
        return

    _call_django('api/war/withdraw/', 'POST', {'id': war_id, 'writer': writer_nick})

    phenny.say('OK, ik schrap je uit de deelnemerslijst, %s.' % writer_nick)

withdraw.commands = ['withdraw']


def participate(phenny, input):
    writer_nick = input.nick
    args = input.group(2)
    if not args:
        phenny.say('Ja, maar waaraan wil je deelnemen, %s? %s' % (writer_nick, random.choice(CONTESTS)))
        return
    war_id = _get_warid(phenny, args, writer_nick)
    if not war_id:
        return

    war_info = _call_django('api/war/info/', 'POST', {'id': war_id})

    if not war_info:
        phenny.say('Die war ken ik niet, %s' % writer_nick)
        return

    participants = _call_django('api/war/listparticipants/', 'POST', {'id': war_id})

    if writer_nick in participants:
        phenny.say('Geen zorgen %s, ik was nog niet vergeten dat je meedoet :-)' % writer_nick)
        return

    _call_django('api/war/participate/', 'POST', {'id': war_id, 'writer': writer_nick})

    phenny.say('OK, ik verwittig je persoonlijk 10 seconden voordat war %s begint, en nog eens wanneer de war eindigt, %s' % (war_id, writer_nick))

participate.commands = ['participate']

if __name__ == '__main__':
    print __doc__.strip()
