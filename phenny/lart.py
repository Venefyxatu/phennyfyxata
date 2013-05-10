#!/usr/bin/env python
# coding=utf-8

import time
import random
from collections import deque

insults = []
insultCache = deque()
maxCacheSize = 5
insultStore = "/opt/projects/evilphenny/lartstore.txt"

def adjust(phenny, arguments, asker):
    if not arguments or arguments.lower() in ["phenny", "phennyfyxata"]:
        arguments = asker

    action = chr(1)+"ACTION "

    chosen = random.choice(insults)

    while chosen in insultCache:
        chosen = random.choice(insults)

    if len(insultCache) > maxCacheSize:
        insultCache.popleft()

    insultCache.append(chosen)

    phenny.say(action + chosen % arguments)

def addTool(phenny, arguments):
    if not '##' in arguments:
        phenny.say("Zorg ervoor dat je ## gebruikt in je lart - zo weet ik waar ik de nickname moet zetten.")
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
    arguments = input.group(2)
    command = input.group(1)

    if command == "lart":
        adjust(phenny, arguments, input.nick)
    elif command == "addlart" and input.owner:
        addTool(phenny, arguments)

def setup(self):
    global insults

    f = open(insultStore, 'r')
    try:
        insults = f.read().split('\n')
    finally:
        f.close()


lart.commands = ["lart", "addlart"]
lart.example = '.lart username'

if __name__ == '__main__':
    print __doc__.strip()
