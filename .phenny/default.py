name = 'Phennyfyxata. http://phenny.venefyxatu.be'
nick = 'Phennyfyxata'
host = 'irc.freenode.net'
channels = ['#dutchnano', '#venefyxatu']
#channels = ['#venefyxatu']
owner = 'venefyxatu'
password = 'PLACEHOLDER_PASSWORD'

# This isn't implemented yet:
# serverpass = 'yourserverpassword'

# These are people who will be able to use admin.py's functions...
admins = [owner] # strings with other nicknames
# But admin.py is disabled by default, as follows:
#exclude = ['admin']

# If you want to enumerate a list of modules rather than disabling
# some, use "enable = ['example']", which takes precedent over exclude
# 
# enable = []

# Directories to load opt modules from
extra = []

# Services to load: maps channel names to white or black lists
external = { 
   '#dutchnano': ['!'], # allow all
   '#venefyxatu': ['!'],
   '#conservative': [], # allow none
   '*': ['py', 'whois', 'glyph'], # default whitelist
}

# EOF


tell_filename = "/home/venefyatu/tellfile"
