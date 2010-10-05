from django.conf.urls.defaults import *

urlpatterns = patterns('phennyfyxata.scores.views', 
        url(r'^$', 'goToWars'),
        url(r'^writers/(?P<nickname>.+)/registerscore/$', 'registerScore'),
        url(r'^writers/(?P<nickname>.+)/overview/$', 'singleWriterOverview'),
        url('^writers/$', 'writersOverview'),
        url('^wars/$', 'warsOverview'),
        url('^wars/(?P<war_id>\d+)/overview/$', 'singleWarOverview'),
        url('^wars/new/$', 'createWar'),
        url('^documentation/$', 'documentation'),
        url('^documentation/nl/$', 'documentationDutch'),
    )
