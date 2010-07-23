from django.conf.urls.defaults import *

urlpatterns = patterns('phennyfyxata.scores.views', 
        url(r'^(?P<writer>.+)/registerscore/$', 'registerscore'),
        url(r'^writers/getallscores/$', 'getallscores'),
        url('^writers/$', 'overview'),
    )
