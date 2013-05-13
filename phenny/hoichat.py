#!/usr/bin/env python
# coding=utf-8

import time
import random

def hoichat(phenny, input): 
    """
    Hoi chat
    """
    greetings = ['Hoi', 'Hallo', 'Hey', 'Dag', 'Wees gegroet,', 'Allo', 'Yo', 'Hai', 'Bonjour', 'Howdi', 'Hee']
    phenny.say("%s %s" % (random.choice(greetings), input.nick))


hoichat.rule = r'^([Hh][AaOo][Ii]|[Hh]([Ee]|[Aa])[Ll]{2}[Oo]) ([Cc][Hh][Aa][Tt]|[Ii][Ee][Dd][Ee][Rr][Ee]{2}[Nn]|[Pp]henny(fyxata)?).*$'

if __name__ == '__main__': 
    print __doc__.strip()
