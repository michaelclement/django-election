from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import make_aware
from django.db.models import Sum
from .models import WordleSubmission, Submitter

import re
from datetime import datetime, timedelta
import calendar

WORDLE_START_DATE = datetime(2021, 6, 19)

def helper__get_week_dates():
    # Get datetime objects for start/end dates of week
    date = datetime.today()
    # Week starts on Sunday
    week_start = date.strptime(f"{date.strftime('%Y')}-W{date.strftime('%V')}-1", "%Y-W%W-%w") - timedelta(days=1)
    diff = timedelta(days=7)
    # Return start date, finish date, and week number
    return week_start, week_start + diff, date.strftime('%V')

def helper__get_puzzles_in_date_range(start_date, window_size=7):
    # Get list of all puzzle nums that are contained in a given
    # start date + window. E.g., a sunday + 7 gives us all puzzles in 
    # that week. 
    # Return list of puzzle numbers.

    puzzle_num_start = (start_date - WORDLE_START_DATE).days
    return [num for num in range(puzzle_num_start, puzzle_num_start + window_size)]

def helper__get_color_breakdown(window='all', submitter='all'):
    # TODO: do we really need this function?
    y_sum = None
    g_sum = None
    submitter_guess_total = None
    WORDLE_PUZZLE_NUM_TODAY = (datetime.today() - WORDLE_START_DATE).days

    # add a model for color data and just pull it here
    if window == 'week':
        week_start, week_finish, week = helper__get_week_dates()

        if submitter != 'all':
            weekly_puzzles = WordleSubmission.objects.filter(
                wordle_number__in = helper__get_puzzles_in_date_range(week_start),
                submitter=submitter.id
            )

            submitter_guess_total = weekly_puzzles.aggregate(Sum('num_guesses'))['num_guesses__sum']
        else:
            weekly_puzzles = WordleSubmission.objects.filter(
                wordle_number__in = helper__get_puzzles_in_date_range(week_start),
            )

        y_sum = weekly_puzzles.aggregate(Sum('valid_wrong_position'))['valid_wrong_position__sum']
        g_sum = weekly_puzzles.aggregate(Sum('valid_right_position'))['valid_right_position__sum']
        b_sum = weekly_puzzles.aggregate(Sum('invalid'))['invalid__sum']

    elif window == 'today':
        latest_submission_list = WordleSubmission.objects.filter(wordle_number = WORDLE_PUZZLE_NUM_TODAY).order_by('-date_submitted')
        y_sum = latest_submission_list.aggregate(Sum('valid_wrong_position'))['valid_wrong_position__sum']
        g_sum = latest_submission_list.aggregate(Sum('valid_right_position'))['valid_right_position__sum']
        b_sum = latest_submission_list.aggregate(Sum('invalid'))['invalid__sum']

    else:
        y_sum = WordleSubmission.objects.aggregate(Sum('valid_wrong_position'))['valid_wrong_position__sum']
        g_sum = WordleSubmission.objects.aggregate(Sum('valid_right_position'))['valid_right_position__sum']
        b_sum = WordleSubmission.objects.aggregate(Sum('invalid'))['invalid__sum']

    return {
        "incorrect_pos_total": y_sum, 
        "correct_pos_total": g_sum,
        "invalid": b_sum,
        "green_percent": int((g_sum / (y_sum + g_sum + b_sum))*100) if None not in [y_sum, g_sum, b_sum] else '',
        "submitter_guess_total": submitter_guess_total,
    }

def helper__get_ranking_of_window(puzzle_list):
    # puzzle_list is a list of puzzle numbers, e.g., [882, 883, ...]

    submitters = Submitter.objects.all()
    min_score = len(puzzle_list)*6

    champs = [] # we can have a tie of champs
    sorted_list = [] # for set of all participants

    for person in submitters:
        date = datetime.today()
        week = date.strftime("%V")

        week_start, week_finish, week_num = helper__get_week_dates()
        subs_for_person = WordleSubmission.objects.filter(
            wordle_number__in = puzzle_list,
            submitter=person
        ).order_by('-wordle_number')

        individual_total = 0
        for sub in subs_for_person:
            individual_total += sub.num_guesses

        # Account for days not yet submitted
        for i in range(len(puzzle_list) - len(subs_for_person)):
            individual_total += 6

        if individual_total < min_score and individual_total > 0 and individual_total < min_score - 1:
            min_score = individual_total
            champs = [person.name]
        elif individual_total == min_score and individual_total < min_score - 1:
            # we have a tie
            champs.append(person.name)

        # Collect everyone's score so we can rank overall
        sorted_list.append({"name": person.name, "total": individual_total})

    # Ranking of all players for given time window, sorted best to worst
    sorted_list = sorted(sorted_list, key=lambda s: s['total'])

    return {"min_score": min_score, "champs": champs, "all_scores": sorted_list}

def helper__get_first_index(target_string):
    for index, char in enumerate(target_string):
        if char in f'\U00002B1B\U0001f7e8\U0001f7e9\U00002b1c':
            return index

# Create your views here.
def index(request):
    WORDLE_PUZZLE_NUM_TODAY = (datetime.today() - WORDLE_START_DATE).days
    latest_submission_list = WordleSubmission.objects.filter(wordle_number = WORDLE_PUZZLE_NUM_TODAY).order_by('-date_submitted')
    submitters = Submitter.objects.all().order_by('name')
    week_start, week_finish, week_num = helper__get_week_dates()

    context = {
        "latest_submission_list": latest_submission_list,
        "submitters": submitters,
        "weekly_champ": helper__get_ranking_of_window(
            helper__get_puzzles_in_date_range(week_start)
        ),
        "yg_breakdown_day": helper__get_color_breakdown('today'),
        "yg_breakdown_week": helper__get_color_breakdown('week'),
        "yg_breakdown_all": helper__get_color_breakdown(),
        "week_start_date": week_start,
        "week_finish_date": week_finish,
        "week_num": week_num,
    }

    return render(request, "portal/index.html", context)

def detail(request, submission_id):
    submission = get_object_or_404(WordleSubmission, pk=submission_id)
    return render(request, "portal/detail.html", {"submission": submission})

def results(request, submitter_id):
    response = "You're looking at results for submitter %s."
    return HttpResponse(response % submitter_id)

def all_weekly_submissions(request):
    delta = timedelta(days=7)
    week_start, week_finish, week_num = helper__get_week_dates()

    latest_submission_list = WordleSubmission.objects.filter(
        wordle_number__in = helper__get_puzzles_in_date_range(week_start)
    ).order_by('-wordle_number')

    submitters = Submitter.objects.all().order_by('name')

    all_submissions = {} 
    for submitter in submitters:
        all_submissions[submitter.name] = {'submissions': [], 'personal_stats': {}}
        results = helper__get_color_breakdown(window='week', submitter=submitter)
        all_submissions[submitter.name]['personal_stats'] = results
        submitter_puzzles = [puzzle for puzzle in latest_submission_list if puzzle.submitter == submitter]
        all_submissions[submitter.name]['submissions'].append(submitter_puzzles)
    
    context = {
        "submitters": submitters,
        "week_num": week_num,
        "current_week_all_nums": helper__get_puzzles_in_date_range(week_start),
        "all_submissions": all_submissions,
    }

    return render(request, "portal/historical-data.html", context)

def vote(request):
    # Hacky workaround to enable two forms on index page... 
    if 'wordle_submission_id' in request.POST.keys():
        return react(request)

    submitter = get_object_or_404(Submitter, pk=request.POST["submitter"])

    target_string = request.POST["submission_text"]
    # Replace "X/6" with "7/6" if they failed to solve puzzle
    target_string = target_string.replace('X', '7')

    re_result = re.search(r"^\D*(\d+).*(\d)\/", target_string)

    # Emoji regexes
    black_reg = re.compile(f'[\U00002B1B\U00002B1C]')
    yellow_reg = re.compile(f'[\U0001f7e8]')
    green_reg = re.compile(f'[\U0001f7e9]') 

    earliest_idx = helper__get_first_index(target_string)

    new_submission = WordleSubmission(
        submission_text = target_string[earliest_idx:].strip(),
        submitter=submitter,
        wordle_number=re_result.group(1),
        num_guesses=re_result.group(2),
        invalid=len(black_reg.findall(target_string)),
        valid_wrong_position=len(yellow_reg.findall(target_string)),
        valid_right_position=len(green_reg.findall(target_string))
    )

    # Make sure we aren't saving a duplicate:
    pre_existing = WordleSubmission.objects.all().filter(
        wordle_number=new_submission.wordle_number, 
        submitter=new_submission.submitter
    )
    if len(pre_existing) <= 0:
        new_submission.save()

    return HttpResponseRedirect("/portal")

def react(request):
    # Get the submission we're reacting to
    wordle_submission = get_object_or_404(WordleSubmission, pk=request.POST["wordle_submission_id"])

    rpk = request.POST.keys()
    if "reaction_0" in rpk:
        wordle_submission.sad_reactions += 1
    elif "reaction_1" in rpk:
        wordle_submission.mind_blown_reactions += 1
    elif "reaction_2" in rpk:
        wordle_submission.wow_reactions += 1
    elif "reaction_3" in rpk:
        wordle_submission.clap_reactions += 1
    else:
        wordle_submission.monkey_reactions += 1

    # Update
    wordle_submission.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def leaderboard(request):
    # TODO: does the calendar module add too much bloat for such a simple task?
    start_of_month = datetime.today().replace(day=1)
    days_in_month = calendar.monthrange(start_of_month.year, start_of_month.month)[1]

    all_puzzles_in_month = helper__get_puzzles_in_date_range(start_of_month, days_in_month)
    scores = helper__get_ranking_of_window(all_puzzles_in_month)

    context = {
        'scores': scores,
        'month_name': start_of_month.strftime('%B'),
        'possible_guesses': len(all_puzzles_in_month) * 6,
        'num_puzzles': len(all_puzzles_in_month),
    }

    return render(request, "portal/leaderboard.html", context)
