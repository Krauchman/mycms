from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone
from .models import Contest, Participant


@login_required(redirect_field_name='login-page')
def info(request, contest_pk):
    contest = get_object_or_404(Contest, pk=contest_pk)

    if not contest.is_active:
        raise Http404("Contest is not active!")
    if not list(Participant.objects.filter(user=request.user, contest=contest)):
        messages.error(request, 'You are not registered for the contest.')
        return redirect('main-page')

    contest_state = contest.get_state()
    seconds = contest_state[1].seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    contest_state = contest_state[0], '%d:%02d:%02d' % (hours, minutes, seconds)
    problems = contest.problem_set.all()
    
    context = {
        'problems': problems,
        'score': get_object_or_404(Participant, user=request.user, contest=contest).points,
        'contest': contest,
        'username': request.user.username,
        'current_time': datetime.now(timezone.utc),
        'contest_state': contest_state,
        'STATE': Contest.STATE,
    }
    return render(request, 'contests/info.html', context)


@login_required(redirect_field_name='login-page')
def ranking(request, contest_pk):
    cur_contest = get_object_or_404(Contest, pk=contest_pk)
    participants = list(Participant.objects.filter(contest__title=cur_contest.title).order_by(
        '-points',
        'user__username'
    ))
    context = {
        'participants': participants,
    }
    return render(request, 'contests/ranking.html', context)


def contest_list(request):
    context = {
        'contest_list': Contest.objects.exclude(is_active=False),
    }
    return render(request, 'contests/contest_list.html', context)
