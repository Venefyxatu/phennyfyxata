#!/usr/bin/env python
# coding=utf-8

import os

import re
import time
import urllib
import urllib2

_LOCKPATH = os.path.join('/', 'RAID', 'sandbox', 'phenny', 'locks')
_TIME_FORMAT = "%H:%M"

padzeroes = lambda x: (4 - len(str(x))) * '0'
splittime = lambda t: (int(t[0:2]), int(t[2:4]))
formatepoch = lambda x: time.strftime(_TIME_FORMAT, time.localtime(x))
applicabletime = lambda x: x != 'busy'

class ArgumentFormatError(Exception):
    def __str__(self):
        return repr(self.args[0])

class ArgumentCountError(Exception):
    def __str__(self):
        return repr(self.args[0])

class ArgumentTypeError(Exception):
    def __str__(self):
        return repr(self.args[0])

class ArgumentOrderError(Exception):
    def __str__(self):
        return repr(self.args[0])

class ArgumentSanitiser:
    def sanitise(self, argumentString):
        splitArguments = argumentString.split()
        splitArguments = self.argumentsToLowerCase(splitArguments)
        if 'busy' in splitArguments:
            splitArguments = self.orderArguments(splitArguments)

        return splitArguments

    def argumentsToLowerCase(self, arguments):
        result = list()
        for arg in arguments:
            result.append(arg.lower())

        return result

    def orderArguments(self, arguments):
        arguments.sort(reverse=True)
        return arguments

class ArgumentValidator:
    def validate(self, arguments):
        if arguments[0] == arguments[1]:
            raise ArgumentFormatError("Very funny, but I don't do 0-seconds wars. You don't either and you know it ;-)")
        self.checkParameterCount(arguments)
        for arg in arguments:
            self.checkCorrectFormat(arg)

        self.checkArgumentOrder(arguments)

    def checkParameterCount(self, arguments):
        if len(arguments) != 2:
            print "Didn't get two parameters."
            raise ArgumentCountError("You need to tell me when the war starts and when it ends, like so : .war 15:00 15:15.")

    def checkCorrectFormat(self, argument):
        if argument == 'busy':
            return

        time_regex = "^(([0]?[0-9]|1[0-9]|2[0-3]):[0-5]?[0-9])$"
        format_regex = re.compile(time_regex)
        if not re.match(format_regex, argument):
            raise ArgumentFormatError("%s is not a correct time (use hh:mm)." % argument)

    def checkArgumentOrder(self, arguments):
        if 'busy' in arguments and arguments.index('busy') != 0:
            raise ArgumentOrderError('"Busy" is no time for a lady to end a war.')

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
    phenny.say("I'll also keep score when the war is done. Just say .score <count> and I'll record it to your nickname.")

def lock(lockName):
    f = open(os.path.join(_LOCKPATH, lockName), 'w')
    f.close()

def registerScore(phenny, arguments, user):
    phenny.say("Registering score %s for %s" % (arguments, user))

    djangoUrl = "http://127.0.0.1:8000/%s/registerscore" % user
    urldata{"score": arguments[0]}

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

    if command == "score":
        try:
            registerScore(phenny, arguments, input.nick)
            return 
        except ArgumentCountError, e:
            phenny.say(e.__str__())
            return

    argSanitiser = ArgumentSanitiser()
    splitArguments = argSanitiser.sanitise(arguments)

    try:
        print "Unvalidated arguments"
        argValidator = ArgumentValidator()
        argValidator.validate(splitArguments)
        print "Arguments validated"
    except ArgumentFormatError, e:
        phenny.say(e.__str__())
        return
    except ArgumentCountError, e:
        phenny.say(e.__str__())
        return
    except ArgumentTypeError, e:
        phenny.say(e.__str__())
        return
    except ArgumentOrderError, e:
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

phennyfyxata.commands = ['war', 'score']
phennyfyxata.example = '.war 1500 1515'

if __name__ == '__main__': 
    print __doc__.strip()
