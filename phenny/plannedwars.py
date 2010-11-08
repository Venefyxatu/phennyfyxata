#!/usr/bin/env python
# coding=utf-8

import time
import urllib
import urllib2

def plannedwars(phenny, input): 
    """ Ik zal een overzicht geven van de wars die nog moeten komen """
    # Print statement to work around a bug when input.group(2) doesn't exist
    print "%s New command received in plannedwars module" % time.localtime()
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

    djangoUrl = "http://phenny.venefyxatu.be/wars/planned/"

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(djangoUrl)
    request.add_header('Content-Type', 'text/http')
    request.get_method = lambda: 'GET'
    url = opener.open(request)
    planned_wars = url.read()
    if planned_wars:
        phenny.say("Deze wars zijn nog gepland:")
    else:
        phenny.say("Er zijn geen wars gepland")
        return
    for war in planned_wars.split(','):
        phenny.say(war)
    return

plannedwars.commands = ["plannedwars"]
plannedwars.example = '.plannedwars'

if __name__ == '__main__': 
    print __doc__.strip()
