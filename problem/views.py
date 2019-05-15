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
        form = SubmitForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.participant = request.user.participant_set.get(contest__pk=contest_pk)
            sub.sent_date = timezone.now()
            sub.problem = get_object_or_404(Problem, problem_id=problem_pk)
            problem_infos = ProblemInfo.objects.filter(problem=get_object_or_404(Problem, problem_id=problem_pk), contest__pk=contest_pk)
            if problem_infos:
                sub.problem_info = problem_infos.first()
            sub.contest = Contest.objects.get(pk=contest_pk)
            sub.save()

            evaluate_submission.delay(sub.pk)

            return redirect('problem-page', contest_pk=contest_pk, problem_pk=problem_pk)
    else:
        form = SubmitForm()
    
    participant = get_object_or_404(Participant, user=request.user)
    contest = get_object_or_404(Contest, pk=contest_pk)
    problem = get_object_or_404(Problem, problem_id=problem_pk, contests=contest)
    submissions = Submission.objects.filter(contest=contest, problem=problem, participant=participant)
    subtasks = problem.subtask_set.all()
    run_infos = RunInfo.objects.filter(submission__in=list(submissions))
    runSubtask_infos = RunSubtaskInfo.objects.filter(submission__in=list(submissions), subtask__in=list(subtasks))
    total = 0
    for score in subtasks:
        total += score.points

    print(runSubtask_infos)
    # print(RunInfo.objects.all().first().submission.source)
    context = {
        'statement': problem.statement,
        'samples': problem.test_set.filter(in_statement=True),
        'form': form,
        'contest': contest,
        'problems': contest.problem_set.all(),
        'submissions': submissions,
        'subtasks': subtasks,
        'run_infos': run_infos,
        'total': total,
        'runSubtask_infos': runSubtask_infos,
    }

    return render(request, 'problem/problem.html', context)
