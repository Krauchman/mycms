from django.shortcuts import render, get_object_or_404, redirect
from .models import Problem
from contest.models import Contest
from django.utils import timezone

from submission.models import Submission, RunInfo, RunSubtaskInfo
from submission.tasks import evaluate_submission
from submission.forms import SubmitForm
from problem.models import ProblemInfo
from contest.models import Contest, Participant

def problem_page(request, contest_pk, problem_pk):
    if request.method == "POST":
        lang = request.POST.get("sub_language")
        source = request.POST.get("sub_source")
        if lang and source:
            sub = Submission(source=source,language=lang)
            sub.participant = request.user.participant_set.get(contest__pk=contest_pk)
            sub.sent_date = timezone.now()
            sub.problem = get_object_or_404(Problem, problem_id=problem_pk)
            problem_infos = ProblemInfo.objects.filter(problem=get_object_or_404(Problem, problem_id=problem_pk), contest__pk=contest_pk)
            if problem_infos:
                sub.problem_info = problem_infos.first()
            sub.contest = Contest.objects.get(pk=contest_pk)
            sub.save()

<<<<<<< HEAD
            evaluate_submission.delay(sub.pk)

            return redirect('submission-page', contest_pk=contest_pk, sub_pk=sub.pk)
    else:
        form = SubmitForm()
    
    contest = get_object_or_404(Contest, pk=contest_pk)
    problem = get_object_or_404(Problem, problem_id=problem_pk, contests=contest)
    context = {
        'statement': problem.statement,
        'samples': problem.test_set.filter(in_statement=True),
        'form': form,
=======
            evaluate_submission.delay(sub_pk = sub.pk, username = request.user.username)

            return redirect('problem-page', contest_pk=contest_pk, problem_pk=problem_pk)
    
    participant = get_object_or_404(Participant, user=request.user)
    contest = get_object_or_404(Contest, pk=contest_pk)
    problem = get_object_or_404(Problem, problem_id=problem_pk, contests=contest)
    submissions = Submission.objects.filter(contest=contest, problem=problem, participant=participant)
    subtasks = problem.subtask_set.all()
    total = 0
    for score in subtasks:
        total += score.points

    # print(RunInfo.objects.all().first().submission.source)
    context = {
        'statement': problem.statement,
        'samples': problem.test_set.filter(in_statement=True),
        'contest': contest,
        'problems': contest.problem_set.all(),
        'submissions': submissions,
        'subtasks': subtasks,
        'total': total,
        'username': request.user.username,
>>>>>>> demo-frontend
    }

    return render(request, 'problem/problem.html', context)
