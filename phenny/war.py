#!/usr/bin/env python
# coding=utf-8

import os

import time
import urllib
import urllib2
import datetime

from validation import _WAR_COMMAND, _SCORE_COMMAND
from validation import PhennyError
from validation import ArgumentCountError
from validation import ArgumentTypeError
from validation import ArgumentSanitiser
from validation import ArgumentValidator

_LOCKPATH = os.path.join('/', 'RAID', 'sandbox', 'phenny', 'locks')
_TIME_FORMAT = "%H:%M"

padzeroes = lambda x: (4 - len(str(x))) * '0'
splittime = lambda t: (int(t[0:2]), int(t[2:4]))
formatepoch = lambda x: time.strftime(_TIME_FORMAT, time.localtime(x))
applicabletime = lambda x: x != 'busy'
duration = lambda x, y: int((y - x) / 60)

class War:
    def __init__(self, phenny, startEpoch=None, endEpoch=time.time()+10):
        self._phenny = phenny
        if startEpoch:
            if not isinstance(startEpoch, float):
                raise ArgumentTypeError("startEpoch should be a float")
            self._startEpoch = startEpoch
        else:
            self._startEpoch = time.time()
        if not isinstance(endEpoch, float):
            raise ArgumentTypeError("endEpoch should be a float")
        self._endEpoch = endEpoch

        if self._endEpoch < time.time():
            print "endEpoch is in the past"
            return


        djangoUrl = "http://phenny.venefyxatu.be/wars/new/"

        urldata = {
                "starttime": self._startEpoch,
                "endtime": self._endEpoch}

        print "Opening url"

        url = openUrl(djangoUrl, urldata)
        print "Done"
        self.id = url.read()

    def signalStart(self):
        epochlock = os.path.join(_LOCKPATH, "start_%s" % str(self._startEpoch))
        if os.path.exists(epochlock):
            try:
                os.remove(epochlock)
            except OSError:
                pass

            waitTime = int(self._startEpoch) - int(time.time()) - 3
            time.sleep(waitTime > 0 and waitTime or 0)

            self._phenny.say('3')
            time.sleep(1)
            self._phenny.say('2')
            time.sleep(1)
            self._phenny.say('1')
            time.sleep(1)

            self._phenny.say("Het is %s volgens mijn uurwerk. Veel succes!" % formatepoch(self._startEpoch))
            self._phenny.say("----------START----------")
        self._phenny.say("War %s (tot %s, %s minuten dus) is begonnen" % (self.id, formatepoch(self._startEpoch), duration(self._startEpoch, self._endEpoch)))

    def waitForWarEnd(self):
        epochlock = os.path.join(_LOCKPATH, "stop_%s" % str(self._endEpoch))
        if os.path.exists(epochlock):
            os.remove(epochlock)
            time.sleep(self._endEpoch - time.time())
            self._phenny.say("---------STOP---------")
        self._phenny.say("War %s is voorbij (%s - %s). Je kan je score registereren met .score %s <score>" % (self.id, formatepoch(self._startEpoch), formatepoch(self._endEpoch), self.id))
        self._phenny.say("Een overzichtje kan je vinden op http://phenny.venefyxatu.be/wars/%s/overview/" % self.id)

    def endWar(self):
        f = open(os.path.join(_LOCKPATH, "stop_%s" % str(self._endEpoch)), 'w')
        f.close()

        if self._endEpoch < time.time():
            self._phenny.say("Deze war is al voorbij. Je bent te laat :(")
            return

        self._phenny.say("Dit wordt war %s" % self.id)
        self._phenny.say("Ik zal het stopsein geven om %s." % formatepoch(self._endEpoch))

        self.waitForWarEnd()

def convertToEpoch(timeToConvert, nextDay = False):
    resultHour, resultMin = timeToConvert.split(':')
    lt = time.localtime()
    resultEpoch = time.mktime((lt[0], lt[1], lt[2], int(resultHour), int(resultMin), 0, lt[6], lt[7], lt[8]))
    if resultEpoch < time.time() or nextDay:
        # Set nextDay to True if we have a timestamp that is in the past. 
        # e. g. if we have a starttime in the past, this is a simple way to flag that the endtime needs to be in the past as well
        nextDay = True
        day = (24*60)*60
        tomorrow = datetime.datetime.fromtimestamp(time.time() + day)
        resultEpoch = time.mktime((tomorrow.year, tomorrow.month, tomorrow.day, int(resultHour), int(resultMin), 0, tomorrow.weekday(), 0, lt[8]))
    return resultEpoch, nextDay

def showHelp(phenny):
    phenny.say("Ik zal je vertellen wanneer je moet starten en stoppen met schrijven als je mij een begin- en einduur geeft.")
    phenny.say("Zorg ervoor dat je het 24-uren formaat gebruikt, want anders raak ik in de war.")
    phenny.say("bv. als je een war wil tussen 15:00 en 15:15, dan zeg je .war 15:00 15:15")
    phenny.say("Als ik gewoon het stopsignaal moet geven gebruik je het woordje 'busy' in plaats van een starttijd")
    phenny.say("Ik kan ook je score bijhouden. Daarvoor zeg je gewoon .%s <war nr> <score> en ik schrijf 'm op samen met je nick." % _SCORE_COMMAND)
    phenny.say("Je kan de scores bekijken op http://phenny.venefyxatu.be")

def lock(lockName):
    f = open(os.path.join(_LOCKPATH, lockName), 'w')
    f.close()

def registerScore(phenny, arguments, user):
    print "Registering score %s for %s" % (arguments, user)

    djangoUrl = "http://phenny.venefyxatu.be/writers/%s/registerscore/" % user
    urldata = {"score": arguments[1], "war": arguments[0]}

    try:

        openUrl(djangoUrl, urldata)
    except urllib2.HTTPError, e:
        print e

        phenny.say("Volgens de annalen bestaat war %s niet. Ik verlies geen documenten, dus ik vermoed dat je je vergist met het ID :-) " % arguments[0])
        return

    phenny.say("Score %s geregistreerd voor %s." % (arguments[1], user))

def openUrl(url, urldata):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=urllib.urlencode(urldata))
    request.add_header('Content-Type', 'text/http')
    request.get_method = lambda: 'POST'
    url = opener.open(request)

    return url

def war(phenny, input): 
    """ Met dit commando vraag je me om het start- en stopsein te geven voor een word war. """
    # Print statement to work around a bug when input.group(2) doesn't exist
    print "%s New command received in war module" % time.localtime()
    arguments = input.group(2)
    command = input.group(1)

    # input: 
    #  s = unicode.__new__(cls, text)
    #  s.sender = origin.sender
    #  s.nick = origin.nick
    #  s.event = event
    #  s.bytes = bytes
    #  s.match = match
    #  s.group = match.group
    #  s.groups = match.groups
    #  s.args = args
    #  s.admin = origin.nick in self.config.admins
    #  s.owner = origin.nick == self.config.owner

    #@TODO: countdown to end of war
    #@TODO: Twitter integration

    if not arguments or arguments == 'help':
        showHelp(phenny)
        return 

    argSanitiser = ArgumentSanitiser.create(command)
    splitArguments = argSanitiser.sanitise(arguments)

    try:
        argValidator = ArgumentValidator.create(command)
        argValidator.validate(splitArguments)
    except PhennyError, e:
        phenny.say(e.__str__().lstrip("'").rstrip("'"))
        return

    if command == _SCORE_COMMAND:
        try:
            registerScore(phenny, splitArguments, input.nick)
            return 
        except ArgumentCountError, e:
            phenny.say(e.__str__())
            return

    if 'busy' in splitArguments:
        endTime, nextDay = convertToEpoch(filter(applicabletime, splitArguments)[0])
        war = War(phenny, endEpoch=endTime)
        return war.endWar()


    startepoch, nextDay = convertToEpoch(splitArguments[0])
    endepoch, nextDay = convertToEpoch(splitArguments[1], nextDay)

    if startepoch > endepoch:
        phenny.say("Ik weet niet hoe het met jou zit, maar ik kan niet terugreizen in de tijd om een war te eindigen voordat die begint. Vraag venefyxatu om me een flux capacitor, of nog beter, een vliegende DeLorean, te kopen als je dat *echt* wil.")
        return

    lock(lockName="start_%s" % str(startepoch))
    lock(lockName="stop_%s" % str(endepoch))

    if startepoch < time.time():
        phenny.say("Die starttijd ligt in het verleden - als ik gewoon de war moet stoppen zeg je .war busy <endtime>")
        return

    phenny.say("Ik zal het startsein geven om %s en het stopsein om %s." % (formatepoch(startepoch), formatepoch(endepoch)))
    

    war = War(phenny, startepoch, endepoch)
    war.signalStart()

    war.waitForWarEnd()

war.commands = [_WAR_COMMAND, _SCORE_COMMAND]
war.example = '.%s 15:00 15:15' % _WAR_COMMAND

if __name__ == '__main__': 
    print __doc__.strip()
