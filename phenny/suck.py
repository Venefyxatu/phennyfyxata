#!/usr/bin/env python
# coding=utf-8

import time
import random


ACTION = chr(1) + "ACTION "
AFIN = chr(1)

NICE_CHOICES = ['Aww, ik vind jou lief, %s!',
                ACTION + ' knuffelt %s' + AFIN,
                '%s: jij bent officieel cool!',
                ACTION + ' knuffelt %s plat' +AFIN,
                'lief van je, %s!']


def suck(phenny, input):
    """
    Phenny suckt soms.
    """
    asker = input.nick
    if ('stom' in input.group()
            or 'trut' in input.group().lower()
            or 'bitch' in input.group().lower()
            or 'evil' in input.group().lower()):
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


suck.rule = (r'(?i)(evil)?phenny(fyxata)? (suck(t|s)|zuigt|is '
             '(stom|een trut|een truttebol|een bitch))')


def lief(phenny, input):
    """
    Maar ze is eigenlijk wel lief
    """
    asker = input.nick

    phenny.say(random.choice(NICE_CHOICES) % asker)


lief.rule = (r'(?i)((ik vind phenny(fyxata)? |phenny(fyxata)? is )'
             '(lief|aardig|cool)|ik hou van phenny(fyxata)?).*')

if __name__ == '__main__':
    print __doc__.strip()
