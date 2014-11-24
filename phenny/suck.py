#!/usr/bin/env python
# coding=utf-8

import time
import random


SUCK_CHOICES = ['neemt een heel lang rietje, stopt het in het drankje van %s en zuigt het leeg']


def suck(phenny, input):
    """
    Phenny suckt soms.
    """
    asker = input.nick
    if 'stom' in input.group() or 'trut' in input.group() or 'bitch' in input.group():
        phenny.say('Zusje? Kan jij %s even laten weten wat we daarvan vinden?' % asker)
        return

    if random.random() < 0.3:
        action = chr(1) + "ACTION "
        phenny.say('%s neemt een heel lang rietje' % action)
        time.sleep(0.2)
        phenny.say('%s stopt het in het drankje van %s' % (action, asker))
        time.sleep(0.2)
        phenny.say('%s drinkt het leeg' % action)
        time.sleep(0.2)
        phenny.say('soms wel ja')
        time.sleep(0.2)
    else:
        phenny.say('Zusje? Kan jij %s even laten weten wat we daarvan vinden?' % asker)


suck.rule = r'([Ee][Vv][Ii][Ll])?[Pp][Hh][Ee][Nn]{2}[Yy]([Ff][Yy][Xx][Aa][Tt][Aa])? ([Ss][Uu][Cc][Kk]([Tt]|[Ss])|[Zz][Uu][Ii][Gg][Tt]|is stom|is een trut|is een truttebol|is een bitch).*'

if __name__ == '__main__':
    print __doc__.strip()
