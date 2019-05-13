from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from contest.models import Contest
from problem.models import Problem, ProblemInfo, PolygonAccount


class ContestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # will be executed before all the class test methods
        # all the created objects should not change in test methods
        PolygonAccount.objects.create(name='Account 1', key='key', secret='secret')

    def setUp(self):
        # will be executed every time before class test method
        Contest.objects.create(title='Contest 1', start_time=timezone.now(),
                               end_time=timezone.now() + timezone.timedelta(hours=5))

    def add_problem(self, contest, short_name):
        problem = Problem.objects.create(name=short_name, problem_id=short_name,
                                         polygon_account=PolygonAccount.objects.first())
        ProblemInfo.objects.create(short_name=short_name, problem=problem, contest=contest)

    def test_contest_is_active(self):
        contest = Contest.objects.get(title='Contest 1')
        self.assertTrue(contest.is_active)

    def test_contest_get_state_is_not_started(self):
        contest = Contest.objects.get(title='Contest 1')
        contest.start_time = timezone.now() + timezone.timedelta(hours=1)
        self.assertEqual(contest.get_state()[0], Contest.STATE.NOT_STARTED)

    def test_contest_get_state_is_in_progress(self):
        contest = Contest.objects.get(title='Contest 1')
        self.assertEqual(contest.get_state()[0], Contest.STATE.IN_PROGRESS)

    def test_contest_get_state_is_finished(self):
        contest = Contest.objects.get(title='Contest 1')
        contest.start_time = timezone.now() - timezone.timedelta(hours=1)
        contest.end_time = timezone.now() - timezone.timedelta(seconds=1)
        self.assertEqual(contest.get_state()[0], Contest.STATE.FINISHED)

    def test_generate_problem_short_name_with_no_problems(self):
        contest = Contest.objects.get(title='Contest 1')
        self.assertEqual(contest.generate_problem_short_name(), 'A')

    def test_generate_problem_short_name_with_several_problems(self):
        contest = Contest.objects.get(title='Contest 1')
        self.add_problem(contest, 'A')
        self.add_problem(contest, 'B')
        self.add_problem(contest, 'AA')
        self.add_problem(contest, 'AB')
        self.assertEqual(contest.generate_problem_short_name(), 'AC')

    def test_generate_problem_short_name_with_problem_A(self):
        contest = Contest.objects.get(title='Contest 1')
        self.add_problem(contest, 'A')
        self.assertEqual(contest.generate_problem_short_name(), 'B')

    def test_generate_problem_short_name_with_problem_ZZZ(self):
        contest = Contest.objects.get(title='Contest 1')
        self.add_problem(contest, 'ZZZ')
        self.assertEqual(contest.generate_problem_short_name(), 'AAAA')

    def test_generate_problem_short_name_with_problem_HAFIZZ(self):
        contest = Contest.objects.get(title='Contest 1')
        self.add_problem(contest, 'HAFIZZ')
        self.assertEqual(contest.generate_problem_short_name(), 'HAFJAA')
