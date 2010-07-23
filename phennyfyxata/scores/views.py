from django.http import HttpResponse
from django.shortcuts import render_to_response

from phennyfyxata.scores.models import War
from phennyfyxata.scores.models import Writer
from phennyfyxata.scores.models import ParticipantScore

def registerScore(request, nickname):
    if request.method == 'POST':
        writer, writerCreated = Writer.objects.get_or_create(nick=nickname)
        if writerCreated:
            writer.save()

        score = request.POST['score']
        warId = request.POST['war']

        war, warCreated = War.objects.get_or_create(id=warId)
        if warCreated:
            war.save()
        
        ps, psCreated = ParticipantScore.objects.get_or_create(writer=writer, war=war)
        ps.score = score
        ps.save()


def writersOverview(request):
    writers = Writer.objects.all()
    return render_to_response('scores/writersOverview.html', {'writers': writers})

def getAllScores(request):
    pass

def warsOverview(request):
    wars = War.objects.all()
    return render_to_response('scores/warsOverview.html', {'wars': wars})

def createWar(request):
    war = War.objects.create()
    html = str(war.id)
    return HttpResponse(html)
