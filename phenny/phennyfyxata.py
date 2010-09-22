#!/usr/bin/env python
# coding=utf-8

import os

import time
import urllib
import urllib2

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

class War:
    def __init__(self, phenny, startEpoch=None, endEpoch=time.time()+10):
        self._phenny = phenny
        if startEpoch:
            if not isinstance(startEpoch, float):
                raise ArgumentTypeError("startEpoch should be a float")
            self._startEpoch = startEpoch
        if not isinstance(endEpoch, float):
            raise ArgumentTypeError("endEpoch should be a float")
        self._endEpoch = endEpoch

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

            self._phenny.say("It is %s according to my clock. Good luck!" % formatepoch(self._startEpoch))
            self._phenny.say("----------GO----------")

    def waitForWarEnd(self):
        epochlock = os.path.join(_LOCKPATH, "stop_%s" % str(self._endEpoch))
        if os.path.exists(epochlock):
            os.remove(epochlock)
            time.sleep(self._endEpoch - time.time())
            self._phenny.say("---------STOP---------")

    def endWar(self):
        f = open(os.path.join(_LOCKPATH, "stop_%s" % str(self._endEpoch)), 'w')
        f.close()

        if self._endEpoch < time.time():
            self._phenny.say("This war is already over. You're too late.")
            return

        self._phenny.say("I'll give the stop signal at %s." % formatepoch(self._endEpoch))

        self.waitForWarEnd()

def convertToEpoch(timeToConvert):
    resultHour, resultMin = timeToConvert.split(':')
    lt = time.localtime()
    resultEpoch = time.mktime((lt[0], lt[1], lt[2], int(resultHour), int(resultMin), 0, lt[6], lt[7], lt[8]))
    return resultEpoch

def showHelp(phenny):
    phenny.say("I'll tell you when to start and stop writing if you give me a start- and endtime.")
    phenny.say("Make sure to use 24-hour format times, because I don't understand anything else. I'm dumb like that.")
    phenny.say("e.g. if you want a war between 15:00 and 15:15, say .war 15:00 15:15")
    phenny.say("If you just want me to end a war in progress, use the word 'busy' instead of a starttime.")
    phenny.say("I'll also keep score when the war is done. Just say .%s <count> and I'll record it to your nickname." % _SCORE_COMMAND)

def lock(lockName):
    f = open(os.path.join(_LOCKPATH, lockName), 'w')
    f.close()

def registerScore(phenny, arguments, user):
    phenny.say("Registering score %s for %s" % (arguments, user))

    djangoUrl = "http://127.0.0.1:8000/%s/registerscore/" % user
    urldata = {"score": arguments[1], "war": arguments[0].strip('war')}

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(djangoUrl, data=urllib.urlencode(urldata))
    request.add_header('Content-Type', 'text/http')
    request.get_method = lambda: 'POST'
    url = opener.open(request)

def phennyfyxata(phenny, input): 
    """
    Time a word war
    """

    # Print statement to work around a bug when input.group(2) doesn't exist
    print "New command received"
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
    #@TODO: Keep score

    if not arguments or arguments == 'help':
        showHelp(phenny)
        return 

    argSanitiser = ArgumentSanitiser.create(command)
    splitArguments = argSanitiser.sanitise(arguments)

    try:
        print "Unvalidated arguments"
        argValidator = ArgumentValidator.create(command)
        argValidator.validate(splitArguments)
        print "Arguments validated"
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
        endTime = convertToEpoch(filter(applicabletime, splitArguments)[0])
        war = War(phenny, endEpoch=endTime)
        return war.endWar()


    startepoch = convertToEpoch(splitArguments[0])
    endepoch = convertToEpoch(splitArguments[1])

    lock(lockName="start_%s" % str(startepoch))
    lock(lockName="stop_%s" % str(endepoch))

    if startepoch < time.time():
        phenny.say("Start time is in the past - if you just want me to end the war, say .war busy <endtime> or .war <endtime> busy")
        return

    phenny.say("I'll give the go signal at %s and the stop signal at %s." % (formatepoch(startepoch), formatepoch(endepoch)))
    

    war = War(phenny, startepoch, endepoch)
    war.signalStart()

    war.waitForWarEnd()

phennyfyxata.commands = [_WAR_COMMAND, _SCORE_COMMAND]
phennyfyxata.example = '.%s 1500 1515' % _WAR_COMMAND

if __name__ == '__main__': 
    print __doc__.strip()
