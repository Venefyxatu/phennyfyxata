#!/usr/bin/env python
"""
ping.py - Phenny Sandwich Paker Module
Author: Thomas Hirsch, http://relet.net
"""

import random

action = chr(1) + "ACTION "
afin = chr(1)


def sandwich(phenny, input):
    topping = random.choice(('avocado', 'sla', 'tomato', 'mozzarella', 'spek',
                             'spam', 'pindakaas', 'bratwurst',
                             ', wreedheidsloze, door PeTA goedgekeurde nep cavia',
                             'digitale', 'komkommer', 'tofu',
                             '-maar ietwat aangebrande-', 'recursieve',
                             'banaan', 'roomijs', 'ham&jam', 'tonijn',
                             'dubbele kaas', 'olijf', '..euh.. gewone',
                             'zelf-gemaakte', 'met liefde gemaakte',
                             'standaard', 'zand', 'heksen', 'mega-grote',
                             'rookworst', 'usbstick', 'rookworst-usbstick'))
    print '---'
    phenny.say("%s biedt %s een lekkere %s sandwich aan.%s" % (action,
                                                               input.nick,
                                                               topping,
                                                               afin))
    print '---'

sandwich.commands = ["eten", "noms"]
sandwich.priority = "low"

FOODS = ['katten', 'honden', 'vissen', 'slangen', 'muizen', 'uilen',
         'valken', 'collega-', 'kraanwerkers-', 'circusartiesten',
         'demonen', 'duivels', 'voetballers', 'trombonespelers',
         'astronauten', 'CEO-', 'nepcavia-', 'stripfiguren']


def feed(phenny, article, pet, owner):
    action = chr(1) + "ACTION "

    randomfood = random.choice(FOODS)
    phenny.say(action + 'geeft %s %s van %s een blik %seten' % (article.lower(),
                                                                pet,
                                                                owner,
                                                                randomfood))


def petfood(phenny, input):
    """
    Feed a user's pet
    """
    article = input.group(1)
    pet = input.group(2)
    owner = input.group(3)
    feed(phenny, article, pet, owner)


petfood.rule = r'(?i)(de|het) (.*) van (.*) (heeft|hebben) honger'
petfood.rule = r'([Dd]e|[Hh]et) (.*) van (.*) (heeft|hebben) honger'

if __name__ == '__main__':
    print __doc__.strip()
