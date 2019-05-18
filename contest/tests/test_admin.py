from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from contest.models import Contest
from problem.models import Problem, ProblemInfo, PolygonAccount


class ContestAdminAddProblemsFormTest(TestCase):
    number_of_problems = 5
    number_of_used_problems = 3

    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser('admin1', 'admin1@test.com', 'adminpassword1')
        Contest.objects.create(title='Contest 1', start_time=timezone.now(),
                               end_time=timezone.now() + timezone.timedelta(hours=5))
        polygon_account = PolygonAccount.objects.create(name='account1', key='key1', secret='secret1')

        for problem_id in range(cls.number_of_problems):
            Problem.objects.create(name='problem' + str(problem_id+1), problem_id=str(problem_id + 1),
                                   polygon_account=polygon_account, status=Problem.STATUS.READY)

    def setUp(self):
        contest = Contest.objects.get(pk=1)

        for problem_id in range(self.number_of_used_problems):
            problem = Problem.objects.get(name='problem' + str(problem_id+1))
            ProblemInfo.objects.create(short_name=str(problem_id+1), problem=problem, contest=contest)

    def test_form_lists_all_unused_problems(self):
        self.client.login(username='admin1', password='adminpassword1')
        response = self.client.get(reverse('admin:contest_contest_change', args=[1]))
        contest = Contest.objects.get(pk=1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unused_problems']),
                         self.number_of_problems - self.number_of_used_problems)

        for problem in response.context['unused_problems']:
            self.assertEqual(ProblemInfo.objects.filter(problem=problem, contest=contest).count(), 0)


class ContestAdminAddParticipantsFormTest(TestCase):
    number_of_users = 10  # not including superuser
    number_of_participants = 5

    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser('admin1', 'admin1@test.com', 'adminpassword1')
        Contest.objects.create(title='Contest 1', start_time=timezone.now(),
                               end_time=timezone.now() + timezone.timedelta(hours=5))

        for user_id in range(cls.number_of_users):
            User.objects.create_user('user' + str(user_id + 1), 'user' + str(user_id + 1) + '@test.com',
                                     'password' + str(user_id + 1))

    def setUp(self):
        contest = Contest.objects.get(pk=1)

        for user_id in range(self.number_of_participants):
            user = User.objects.get(username='user' + str(user_id+1))
            contest.participant_set.create(user=user, points=10 * (user_id - (user_id % 2)))

    def test_form_lists_all_nonparticipating_users(self):
        self.client.login(username='admin1', password='adminpassword1')
        response = self.client.get(reverse('admin:contest_contest_change', args=[1]))
        contest = Contest.objects.get(pk=1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['nonparticipating_users']),
                         self.number_of_users - self.number_of_participants + 1)  # +1 for superuser

        for user in response.context['nonparticipating_users']:
            self.assertEqual(contest.participant_set.filter(user=user).count(), 0)
