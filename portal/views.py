from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import make_aware
from django.db.models import Sum
from .models import WordleSubmission, Submitter, Champion

import re
import json
from datetime import datetime, timedelta
import calendar

WORDLE_START_DATE = datetime(2021, 6, 19)

def helper__month_mangler(date=datetime.today().replace(day=1), pad_to_current_day_only=True):
    start_of_month = date
    days_in_month = calendar.monthrange(start_of_month.year, start_of_month.month)[1]

    all_puzzles_in_month = helper__get_puzzles_in_date_range(start_of_month, days_in_month)
    scores = helper__get_ranking_of_window(all_puzzles_in_month, pad_to_current_day_only)

    return start_of_month, days_in_month, all_puzzles_in_month, scores

def helper__get_week_dates():
    # Get datetime objects for start/end dates of week
    date = datetime.today()
    iso_week_date = date.strftime('%V')
    # Week starts on Sunday
    if date.strftime("%A") == 'Sunday':
        iso_week_date = int(iso_week_date) + 1
        week_start = date.strptime(f"{date.strftime('%Y')}-W{iso_week_date}-1", "%Y-W%W-%w") - timedelta(days=1)
    else: # we're part-way into a week
        week_start = date.strptime(f"{date.strftime('%Y')}-W{iso_week_date}-1", "%Y-W%W-%w") - timedelta(days=1)

    # Return start date, finish date, and week number
    return week_start, week_start + timedelta(days=7), iso_week_date

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

def helper__get_ranking_of_window(puzzle_list, pad_to_current_day_only=False):
    # puzzle_list: list of puzzle numbers, e.g., [882, 883, ...]
    # pad_to_current_day_only: indicates whether or not we just want to pad up to 
    #   the current day of the month

    submitters = Submitter.objects.all()
    min_score = (len(puzzle_list)*6)+1

    champs = [] # we can have a tie of champs
    sorted_list = [] # for set of all participants

    for person in submitters:
        subs_for_person = WordleSubmission.objects.filter(
            wordle_number__in = puzzle_list,
            submitter=person
        ).order_by('-wordle_number')

        individual_total = 0
        for sub in subs_for_person:
            individual_total += sub.num_guesses

        # Account for days not yet submitted by "padding" the guess count with
        # 6s on days when the user hasn't submitted a guess yet. 
        #
        # We take two approaches. If the optional argument pad_to_current_day_only is true,
        # we're trying to calculate the champ of the month, in which case we
        # pad up to the current day of the month. Otherwise, we just pad up
        # to the length of puzzle_list
        padding = len(puzzle_list) if not pad_to_current_day_only else datetime.today().day
        for i in range(padding - len(subs_for_person)):
            individual_total += 6

        if individual_total < min_score and individual_total > 0:
            min_score = individual_total
            champs = [person.name]
        elif individual_total == min_score:
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
    week_start, week_finish, week_num = helper__get_week_dates()

    latest_submission_list = WordleSubmission.objects.filter(
        wordle_number__in = helper__get_puzzles_in_date_range(week_start)
    ).order_by('-wordle_number')

    submitters = Submitter.objects.all().order_by('name')

    all_submissions = {} 
    for submitter in submitters:
        all_submissions[submitter.name] = {
            'submissions': [[
                puzzle for puzzle in latest_submission_list if puzzle.submitter == submitter
            ]],
            'personal_stats': helper__get_color_breakdown(
                window='week', submitter=submitter
            )
        }
    
    context = {
        "submitters": submitters,
        "week_num": week_num,
        "current_week_all_nums": helper__get_puzzles_in_date_range(week_start),
        "all_submissions": all_submissions,
    }

    return render(request, "portal/historical-data.html", context)

def vote(request):
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
    post_data = json.load(request)
    pk = post_data['wordle_submission_id']

    # Get the submission we're reacting to
    wordle_submission = get_object_or_404(WordleSubmission, pk=pk)

    res = 0
    if post_data['emojiId'] == 0:
        wordle_submission.sad_reactions += 1
        res = wordle_submission.sad_reactions
    elif post_data['emojiId'] == 1:
        wordle_submission.mind_blown_reactions += 1
        res = wordle_submission.mind_blown_reactions
    elif post_data['emojiId'] == 2:
        wordle_submission.wow_reactions += 1
        res = wordle_submission.wow_reactions
    elif post_data['emojiId'] == 3:
        wordle_submission.clap_reactions += 1
        res = wordle_submission.clap_reactions
    else:
        wordle_submission.monkey_reactions += 1
        res = wordle_submission.monkey_reactions

    # Update
    wordle_submission.save()

    # get the number of each emoji from that sub: 
    return JsonResponse({'reactionList': wordle_submission.reaction_list})

def leaderboard(request):
    # TODO: does the calendar module add too much bloat for such a simple task?
    start_of_month, days_in_month, all_puzzles_in_month, scores = helper__month_mangler()

    # Update list of champions on the first of the month
    if datetime.today().day == 1:
        start_of_last_month = (datetime.today() - timedelta(days=1)).replace(day=1)
        sm, dim, apim, s = helper__month_mangler(start_of_last_month, False)

        submitters = Submitter.objects.all()
        # TODO: allow ties?
        champname = s['all_scores'][0]['name'] # champ of specified month
        champ_submitter = None
        for person in submitters:
            if person.name == champname:
                champ_submitter = person

        # add a new champ for specified month
        sm = sm.replace(hour=0, minute=0, second=0)
        new_monthly_champ = Champion(
            submitter=champ_submitter,
            window_type='month',
            window_start=sm, # start of last month
            window_end=sm + timedelta(days=dim-1), # last day of last month
            num_guesses=s['all_scores'][0]['total'], # top champ score - we choose the alphabetical winner if a tie
            num_possible_guesses=dim*6,
        )
        already_exists = Champion.objects.filter(
            window_start__month=sm.month
        )
        if already_exists.count() == 0:
            new_monthly_champ.save()

    champions = Champion.objects.filter(
        window_type='month',
    ).order_by('-window_start')

    context = {
        'scores': scores,
        'month_name': start_of_month.strftime('%B'),
        'possible_guesses': datetime.today().day * 6, # All guesses up to today
        'num_puzzles': len(all_puzzles_in_month),
        'champions': champions,
    }

    return render(request, "portal/leaderboard.html", context)
