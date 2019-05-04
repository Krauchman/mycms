from django.shortcuts import render, get_object_or_404, redirect
from .models import Problem
from contest.models import Contest
from django.utils import timezone

from submission.models import Submission
from submission.tasks import evaluate_submission
from submission.forms import SubmitForm
from problem.models import ProblemInfo
from contest.models import Contest

def problem_page(request, contest_pk, problem_pk):
    if request.method == "POST":
        form = SubmitForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.participant = request.user.participant_set.get(contest__pk=contest_pk)
            sub.sent_date = timezone.now()
            problem_infos = ProblemInfo.objects.filter(problem=get_object_or_404(Problem, problem_id=problem_pk), contest__pk=contest_pk)
            if problem_infos:
                sub.problem_info = problem_infos.first()
            sub.contest = Contest.objects.get(pk=contest_pk)
            sub.save()

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
    }

    return render(request, 'problem/problem.html', context)
