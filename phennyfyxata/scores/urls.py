from django.conf.urls.defaults import *

urlpatterns = patterns('phennyfyxata.scores.views',
        url(r'^$', 'goToWars'),
        url(r'^writers/(?P<nickname>.+)/registerscore/$', 'registerScore'),
        url(r'^writers/(?P<nickname>.+)/overview/$', 'singleWriterOverview'),
        url('^writers/$', 'writersOverview'),
        url('^wars/$', 'warsOverview'),
        url('^wars/(?P<war_id>\d+)/overview/$', 'singleWarOverview'),
        url('^wars/(?P<war_id>\d+)/info/$', 'singleWarInfo'),
        url('^wars/new/$', 'createWar'),
        url('^wars/active/$', 'activeWars'),
        url('^wars/planned/$', 'plannedWars'),
        url('^wars/withdraw/$', 'withdrawWar'),
        url('^wars/(?P<war_id>\d+)/participate/$', 'participateWar'),
        url('^documentation/$', 'documentation'),
        url('^documentation/nl/$', 'documentationDutch'),
        url('^language/$', 'language'),
    )
