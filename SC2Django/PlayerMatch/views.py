from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import FileFieldForm
from .tasks import process_uploaded_replay, selenium_process_replay
from django.views.generic import TemplateView
from .models import OverallSentiment, PlayerMatchSingular
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse

# Create your views here.


def sentiment_data(request):
    curSentiments = OverallSentiment.objects.get(pk=1)
    terranSent = '{:.2f}'.format(0.00)
    zergSent = '{:.2f}'.format(0.00)
    protossSent = '{:.2f}'.format(0.00)
    if curSentiments.terranSentimentCount != 0:
        terranSent = '{:.2f}'.format(round((curSentiments.terranSentimentOverall / curSentiments.terranSentimentCount) * 100, 2))

    if curSentiments.zergSentimentCount != 0:
        zergSent = '{:.2f}'.format(round((curSentiments.zergSentimentOverall / curSentiments.zergSentimentCount) * 100, 2))

    if curSentiments.protossSentimentCount != 0:
        protossSent = '{:.2f}'.format(round((curSentiments.protossSentimentOverall / curSentiments.protossSentimentCount) * 100, 2))

    return JsonResponse({
        'terran': terranSent,
        'zerg': zergSent,
        'protoss': protossSent
    })


class FileFieldView(FormView):
    form_class = FileFieldForm
    template_name = 'PlayerMatch/replay_file_upload.html'

    def get_success_url(self):
        return reverse('thanks-page')

    def get_context_data(self, **kwargs):

        context = super(FileFieldView, self).get_context_data(**kwargs)
        curSentiments = OverallSentiment.objects.get(pk=1)
        allPlayers = PlayerMatchSingular.objects.order_by('pk').reverse()

        negativeMessages = []
        positiveMessages = []
        for i in allPlayers:
            if len(negativeMessages) >= 100:
                break
            for num in range(0, len(i.messages)):
                if i.messageSentiments[num] < -0.5:
                    negativeMessages.append('"' + i.messages[num] + '"' + "&nbsp;&nbsp;-" + i.username)
                    break

        for i in allPlayers:
            if len(positiveMessages) >= 100:
                break
            for num in range(0, len(i.messages)):
                if i.messageSentiments[num] > 0.5:
                    positiveMessages.append('"' + i.messages[num] + '"' + "&nbsp;&nbsp;-" + i.username)
                    break

        context['curMessages'] = negativeMessages

        context['curMessagesPositive'] = positiveMessages

        terranSent = '{:.2f}'.format(0.00)
        zergSent = '{:.2f}'.format(0.00)
        protossSent = '{:.2f}'.format(0.00)

        if curSentiments.terranSentimentCount != 0:
            terranSent = '{:.2f}'.format(
                round((curSentiments.terranSentimentOverall / curSentiments.terranSentimentCount) * 100, 2))

        if curSentiments.zergSentimentCount != 0:
            zergSent = '{:.2f}'.format(
                round((curSentiments.zergSentimentOverall / curSentiments.zergSentimentCount) * 100, 2))

        if curSentiments.protossSentimentCount != 0:
            protossSent = '{:.2f}'.format(
                round((curSentiments.protossSentimentOverall / curSentiments.protossSentimentCount) * 100, 2))

        context['terran'] = terranSent

        context['zerg'] = zergSent

        context['protoss'] = protossSent

        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('process_btn'):
            selenium_process_replay()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        files = request.FILES.getlist('replay_file')

        if form.is_valid():
            for f in files:
                # Verify Correct Files
                if f.name.endswith('.SC2Replay'):
                    print(f.name)
                    #process_uploaded_replay(f.file)
                    #Use Async in Production
                    process_uploaded_replay.delay(f.file)
                else:
                    return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TerranTableView(TemplateView):
    template_name = 'PlayerMatch/terran_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lastHundred = list(PlayerMatchSingular.objects.filter(curRace="Terran").order_by('-id')[:100])
        context["last_hundred"] = lastHundred

        return context


class ZergTableView(TemplateView):
    template_name = 'PlayerMatch/zerg_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lastHundred = list(PlayerMatchSingular.objects.filter(curRace="Zerg").order_by('-id')[:100])
        context["last_hundred"] = lastHundred

        return context


class ProtossTableView(TemplateView):
    template_name = 'PlayerMatch/protoss_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lastHundred = list(PlayerMatchSingular.objects.filter(curRace="Protoss").order_by('-id')[:100])
        context["last_hundred"] = lastHundred

        return context
