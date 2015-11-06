#!/usr/bin/env python

# roulette.py - a russian roulette for phenny

import random

deaths = ("valt dood.", "ziet er verbaasd uit.", "schiet zichzelf overhoop.",
          "maakt het meubilair vuil.", "- in Soviet Russia, gun levels you.", "nu als spook!", 
          "gaat naar de eeuwige jachtvelden.", "heeft nu hoofdventilatie.", "scoort een punt.",
          "weet nu wat geluk hebben is.", "gaat het hoekje om.", "gaat om zeep", "houdt plots op met ademen", 
          "zou nu wel een gaatjesdichtende kurk kunnen gebruiken", "heeft nu een probleem dat niet zomaar even met wat hoestsiroop opgelost kan worden",
          " - nu met extra lood!")

def setup(self):
  self.roulette={}
  self.roulette['run']=False

def spin(phenny, input):
  gun = phenny.roulette['gun']
  pos = random.randint(0,len(gun)-1)
  gun = gun[pos:]+gun[:pos]
  phenny.roulette['gun']=gun

def rrload(phenny, input):
  if phenny.roulette['run']:
    phenny.say('Eerst leegmaken, dan krijg je nieuwe kogels...')
    return
  bullets = 1
  chambers = 6
  try:
    params = input.split(" ")
    bullets = int(params[1])
    chambers = int(params[2])
  except:
    pass
  chambers = max(2,min(chambers,100))
  bullets = max(1,min(bullets,100))
  if bullets > chambers:
    bullets = chambers
  gun = [False]*chambers
  for bullet in range(0,bullets):
    gun[bullet]=True
  phenny.roulette['gun']=gun
  spin(phenny, input)
  phenny.roulette['run']=True
  strbul = str(bullets) + ((bullets == 1) and " kogel" or " kogels")
  strcha = str(chambers) + ((chambers == 1) and " kamer" or " kamers")
  phenny.say("Hier is een revolver met "+strbul+" in "+strcha+". Do you feel lucky, punk? Huh? Do you?")
rrload.commands=["load"]
rrload.thread=False

def rrspin(phenny, input):
  if phenny.roulette['run']:
    spin(phenny, input)
    phenny.say("RRRRR... ["+input.nick + " draait aan de cylinder.] ...kaCHINK!")
rrspin.commands=["spin"]
rrspin.thread=False

def rrclick(phenny, input):
  if phenny.roulette['run']:
    gun = phenny.roulette['gun']
    next = gun[0]
    if next:
      phenny.say("BLAM! "+input.nick+" "+random.choice(deaths))
      phenny.roulette['run']=False
    else:
      phenny.say("Klik. Er gebeurt niets.")
      gun = gun[1:]+gun[:1]
      phenny.roulette['gun']=gun
  else:
    phenny.say("Er gebeurt niets.")
    phenny.say("Omdat de revolver niet geladen is, duhh!")

rrclick.commands=["pull"]
rrclick.thread=False
