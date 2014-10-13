#!/usr/bin/env python
# coding=utf-8

import random


SUCK_CHOICES = ['neemt een heel lang rietje, stopt het in het drankje van %s en zuigt het leeg']


def suck(phenny, input):
    """
    Phenny suckt soms.
    """
    phenny.say(random.choice(SUCK_CHOICES))


suck.rule = r'[Pp][Hh][Ee][Nn]{2}[Yy] ([Ss][Uu][Cc][Kk]([Tt]|[Ss])|[Zz][Uu][Gg][Tt])'

if __name__ == '__main__':
    print __doc__.strip()
