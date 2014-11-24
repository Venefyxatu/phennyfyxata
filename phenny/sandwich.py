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
    phenny.say(action + "biedt " + input.nick + " een lekkere " + topping + " sandwich aan." + afin)
    print '---'

sandwich.commands = ["eten", "noms"]
sandwich.priority = "low"

FOODS = ['katten', 'honden', 'vissen', 'slangen', 'muizen', 'uilen',
         'valken', 'collega-', 'kraanwerkers-', 'circusartiesten',
         'demonen', 'duivels', 'voetballers', 'trombonespelers',
         'astronauten', 'CEO-', 'nepcavia-', 'stripfiguren']


def feed(phenny, pet, owner):
    action = chr(1) + "ACTION "

    randomfood = random.choice(FOODS)
    phenny.say(action + 'geeft de %s van %s een blik %seten' % (pet,
                                                                owner,
                                                                randomfood))


def petfood(phenny, input):
    """
    Feed a user's pet
    """
    pet = input.group(1)
    owner = input.group(2)
    feed(phenny, pet, owner)


petfood.rule = r'de (.*) van (.*) heeft honger'

if __name__ == '__main__':
    print __doc__.strip()
