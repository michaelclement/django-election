from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import WordleSubmission, Submitter

import re
from datetime import datetime

def helper__get_champion_of_week():
    submitters = Submitter.objects.all()
    total_chances = 42 #(6 chances * 7 days)

    min_score = 43
    min_person = [] # we can have a tie

    for person in submitters:
        date = datetime.today()
        week = date.strftime("%V")
        subs_for_person = WordleSubmission.objects.filter(date_submitted__week=week, submitter=person)
        individual_total = 0
        for sub in subs_for_person:
            individual_total += sub.num_guesses
        if individual_total < min_score:
            min_score = individual_total
            min_person = [person.name]
        elif individual_total == min_score:
            # we have a tie
            min_person.append(person.name)

    return {"min_score": min_score, "min_person": min_person}


def helper__get_first_index(target_string):
    for index, char in enumerate(target_string):
        if char in f'\U00002B1B\U0001f7e8\U0001f7e9':
            return index


# Create your views here.
def index(request):
    latest_submission_list = WordleSubmission.objects.filter(date_submitted__date=datetime.today().date())

    submitters = Submitter.objects.all()
    context = {
        "latest_submission_list": latest_submission_list,
        "submitters": submitters,
        "weekly_champ": helper__get_champion_of_week()
    }
    return render(request, "portal/index.html", context)

def detail(request, submission_id):
    submission = get_object_or_404(WordleSubmission, pk=submission_id)
    return render(request, "portal/detail.html", {"submission": submission})

def results(request, submitter_id):
    response = "You're looking at results for submitter %s."
    return HttpResponse(response % submitter_id)

def vote(request):
    submitter = get_object_or_404(Submitter, pk=request.POST["submitter"])

    # Get the details we want
    target_string = request.POST["submission_text"]
    re_result = re.search(r"^\D*(\d+).*(\d)\/", target_string)

    # Emoji regexes
    black_reg = re.compile(f'[\U00002B1B]')
    yellow_reg = re.compile(f'[\U0001f7e8]')
    green_reg = re.compile(f'[\U0001f7e9]') 

    earliest_idx = helper__get_first_index(target_string)

    new_submission = WordleSubmission(
        submission_text = target_string[earliest_idx-1:],
        submitter=submitter,
        wordle_number=re_result.group(1),
        num_guesses=re_result.group(2),
        invalid=len(black_reg.findall(target_string)),
        valid_wrong_position=len(yellow_reg.findall(target_string)),
        valid_right_position=len(green_reg.findall(target_string))
    )

    new_submission.save()

    return HttpResponseRedirect("/portal")
