from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import F # for avoiding race conditions
from django.utils import timezone

from .forms import TokenForm
from .models import Choice, Question, Token

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, token):
    return render(request, 'polls/vote.html', {
            'token': token,
            'questions': Question.objects.filter(
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
            }
        )

def submit_vote(request, token):
    # TODO: refactor this to use a proper Form class.
    # Currently this enables us to list all questions
    # on a single form and submit them all at once 
    token = get_object_or_404(Token, pk=token)
    if request.method == 'POST' and token.is_valid():
        form = request.POST
        for k in form:
            # Make sure it's not the csrf token
            if ('token' not in k):
                try:
                    question = get_object_or_404(Question, pk=k)
                    choice = question.choice_set.get(pk=form[k])
                except (KeyError, Choice.DoesNotExist):
                    # TODO: error toast

                    # re-enable token if we choke on the form
                    token.token_used = False
                    token.save()
                else:
                    choice.votes = F('votes') + 1
                    choice.save()

        token.token_used = True
        token.save() # render token impotent 
    return render(request, 'polls/complete.html')

def landing_page(request):
    return render(request, 'polls/landing_page.html')

def enter_token(request, valid=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TokenForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            try:
                token = Token.objects.get(pk=form.cleaned_data["token"])
                if token.is_valid():
                    # redirect to a new URL:
                    return HttpResponseRedirect(reverse('polls:vote', args=[token]))
                else:
                    valid = "Token already used."
            except Token.DoesNotExist:
                valid = "Token not found. Was it mistyped?"

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TokenForm()

    return render(request, 'polls/enter_token.html', {'form': form, 'valid': valid})
