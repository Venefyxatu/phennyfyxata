#!/usr/bin/env python
# coding=utf-8

import time
import random
from collections import deque

insults = []
insultCache = deque()
maxCacheSize = 5
insultStore = "/opt/projects/evilphenny/lartstore.txt"

REFUSAL_CHOICES = ['Zou je wel willen he, grapjas?',
                   "Maar... maar... maar... :'(",
                   'In je dromen!',
                   'Yeah, right! Goeie poging!',
                   'Heee, wacht eens even...!',
                   'Oh, hoe gemeen!',
                   'Wat denk je dat ik ben? Dom?',
                   'Ga jij eerst maar een rondje stroopworstelen met een leger mieren, %s!',
                   'Jezelf zal je bedoelen',
                   'Har-de-har har, %s',
                   'Daarvoor heb ik niet genoeg alcohol in me, %s']


def adjust(phenny, arguments, asker):
    print '>%s<' % arguments
    if not arguments or arguments.lower().strip() in ["phenny", "phennyfyxata"]:
        arguments = asker
    elif arguments.lower().strip() in ['vene', 'venefyxatu', 'de chef']:
        phenny.say('Geweld gebruiken tegen de chef, %s? Ben je gek?' % asker)
        return
    elif arguments.lower().strip() in ['evil', 'evilphenny', 'jezelf', 'zichzelf', 'evil phenny']:
        refusal = random.choice(REFUSAL_CHOICES)
        phenny.say(refusal % tuple(asker for x in range(refusal.count('%s'))))
        return

    action = chr(1) + "ACTION "

    chosen = random.choice(insults)

    while chosen in insultCache:
        chosen = random.choice(insults)

    if len(insultCache) > maxCacheSize:
        insultCache.popleft()

    insultCache.append(chosen)

    phenny.say(action + chosen % tuple(arguments for x in range(chosen.count('%s'))))


def addTool(phenny, arguments):
    if not '##' in arguments:
        phenny.say("Zorg ervoor dat je ## gebruikt in je lart - "
                   "zo weet ik waar ik de nickname moet zetten.")
        return

    insults.append(arguments.replace('##', '%s'))

    f = open(insultStore, 'w')
    try:
        f.write('\n'.join(insults))
    finally:
        f.close()


def lart(phenny, input):
    """
    Insult a user
    """
    print "%s New command received in lart module" % time.localtime()
    command = input.group(1)
    if not input.startswith('Zusje'):
        arguments = input.group(2)

    if command == "addlart" and input.owner:
        addTool(phenny, arguments)
        return

    if input.startswith('Zusje?'):
        if input.nick == 'Phennyfyxata':
            adjust(phenny, input.groups()[0], input.nick)
    else:
        adjust(phenny, arguments, input.nick)


def setup(self):
    global insults

    f = open(insultStore, 'r')
    try:
        insults = f.read().split('\n')
    finally:
        f.close()


lart.commands = ["lart", "addlart"]
lart.example = '.lart username'
lart.rule = r'Zusje\? Kan jij (.*) even laten weten wat we daarvan vinden\?'

if __name__ == '__main__':
    print __doc__.strip()
