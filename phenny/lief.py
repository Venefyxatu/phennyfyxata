#!/usr/bin/env python
# coding=utf-8

import random


ACTION = chr(1) + "ACTION "
AFIN = chr(1)

NICE_OPTIONS = ['geeft %s een koekje',
                'knuffelt %s',
                'aait %s over het hoofd',
                'doet een dansje met %s',
                'stopt %s stiekem een stuk chocola toe',
                ('laat een bende kittens los op %s. Tenzij je allergisch bent '
                 'aan katten, dan zijn het puppies.'),
                'masseert de polsen van %s, voor extra typkracht!',
                'geeft %s een stuk cake',
                'maakt een groot bord lekker warme spaghetti voor %s',
                ('stopt een mysterieuze doos in het verhaal van %s, voor '
                 'extra wordcount!'),
                ('geeft %s stiekem een volle balpen, voor de volgende keer '
                 'dat mijn zusje je opsluit'),
                'bestelt pizza voor %s',
                'haalt een warm, comfortabel dekentje uit de kast voor %s',
                ('zet een dienblad met verse koffie, thee en chocomelk '
                 'klaar voor %s'),
                ]

NICE_CHOICES = [ACTION + x + AFIN for x in NICE_OPTIONS]


def aardig(phenny, input):
    """
    Phenny kan ook aardig doen
    """
    target = input.groups()[1] or input.nick
    choice = random.choice(NICE_CHOICES) % target
    phenny.say(choice)


aardig.commands = ['lief']

if __name__ == '__main__':
    print __doc__.strip()
