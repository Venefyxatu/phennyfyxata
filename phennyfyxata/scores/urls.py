from django.conf.urls.defaults import *

urlpatterns = patterns('phennyfyxata.scores.views', 
        url(r'^(?P<nickname>.+)/registerscore/$', 'registerScore'),
        url(r'^writers/getallscores/$', 'getAllScores'),
        url('^writers/$', 'writersOverview'),
        url('^wars/$', 'warsOverview'),
        url('^wars/new/$', 'createWar'),
    )
