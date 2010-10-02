import time
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist

from phennyfyxata.scores.models import War
from phennyfyxata.scores.models import Writer
from phennyfyxata.scores.models import ParticipantScore

def registerScore(request, nickname):
    if request.method == 'POST':
        logging.log(logging.INFO, "POST method found")
        writer, writerCreated = Writer.objects.get_or_create(nick=nickname)
        logging.log(logging.INFO, "Writer is created: %s" % writerCreated)
        if writerCreated:
            writer.save()

        score = request.POST['score']
        warId = request.POST['war']

        logging.log(logging.INFO, "Score is %s. War ID is %s" % (score, warId))

        war, warCreated = War.objects.get_or_create(id=warId)
        if warCreated:
            war.save()
        
        ps, psCreated = ParticipantScore.objects.get_or_create(writer=writer, war=war)
        ps.score = score
        ps.save()
    return HttpResponse("OK")


def goToWars(request):
    return HttpResponseRedirect("/wars/")

def writersOverview(request):
    writers = Writer.objects.all().order_by("nick")
    return render_to_response('scores/writersOverview.html', {'writers': writers})

def singleWriterOverview(request, nickname):
    try:
        writer  = Writer.objects.get(nick=nickname)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWriterOverview.html', {'writer': writer})

def warsOverview(request):
    wars = War.objects.all()
    return render_to_response('scores/warsOverview.html', {'wars': wars})

def singleWarOverview(request, war_id):
    try:
        war = War.objects.get(id=war_id)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWarOverview.html', {'war': war})

def createWar(request):
    logging.log(logging.INFO, "Creating a new war")
    if request.method == 'POST':
        logging.log(logging.INFO, "POST method found in createWar")
        logging.log(logging.INFO, "POST data: %s" % request.POST)
        endtime = request.POST['endtime']
        starttime = request.POST['starttime']
        logging.log(logging.INFO, "Start time is %s (type %s)" % (starttime, type(starttime)))
        logging.log(logging.INFO, "End time is %s (type %s)" % (endtime, type(endtime)))
        war = War.objects.create(timestamp=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(starttime))), endtime=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(endtime))))
        logging.log(logging.INFO, "Created war")
        html = str(war.id)
        return HttpResponse(html)
    raise Http404
