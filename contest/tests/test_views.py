from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from contest.models import Contest


class ContestListViewTest(TestCase):
    number_of_contests = 10
    number_of_active_contests = 8

    @classmethod
    def setUpTestData(cls):
        for contest_id in range(cls.number_of_contests):
            Contest.objects.create(
                title='Contest ' + str(contest_id),
                start_time=timezone.now() + timezone.timedelta(minutes=contest_id*30),
                end_time=timezone.now() + timezone.timedelta(hours=contest_id),
                is_active=(contest_id < cls.number_of_active_contests)
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/contest_list.html')

    def test_view_lists_all_contests(self):
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['contest_list']), self.number_of_active_contests)


class ContestInfoViewTest(TestCase):
    number_of_contests = 10
    number_of_active_contests = 8
    number_of_participated_contests = 4

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('user1', 'user1@test.com', 'password1')
        for contest_id in range(cls.number_of_contests):
            contest = Contest.objects.create(
                title='Contest ' + str(contest_id),
                start_time=timezone.now() + timezone.timedelta(minutes=contest_id*30),
                end_time=timezone.now() + timezone.timedelta(hours=contest_id),
                is_active=(contest_id < cls.number_of_active_contests)
            )

            if contest_id < cls.number_of_participated_contests:
                contest.participant_set.create(user=user)

    def test_view_url_exists_for_participating_user(self):
        self.client.login(username='user1', password='password1')

        for contest_id in range(self.number_of_participated_contests):
            response = self.client.get('/contest/' + str(contest_id+1) + '/')
            self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='password1')

        for contest_id in range(self.number_of_participated_contests):
            response = self.client.get(reverse('contest-info', kwargs={'contest_pk': contest_id+1}))
            self.assertEquals(response.status_code, 200)

    def test_view_requires_authentication(self):
        response = self.client.get(reverse('contest-info', kwargs={'contest_pk': 1}))
        self.assertRedirects(response, reverse('login-page') + '?login-page=/contest/1/')

    def test_view_url_redirects_for_nonparticipating_user(self):
        self.client.login(username='user1', password='password1')

        for contest_id in range(self.number_of_participated_contests, self.number_of_active_contests):
            response = self.client.get(reverse('contest-info', kwargs={'contest_pk': contest_id+1}))
            self.assertRedirects(response, reverse('main-page'))

    def test_view_url_does_not_exist_for_inactive_contest(self):
        self.client.login(username='user1', password='password1')

        for contest_id in range(self.number_of_active_contests, self.number_of_contests):
            response = self.client.get(reverse('contest-info', kwargs={'contest_pk': contest_id+1}))
            self.assertEquals(response.status_code, 404)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='password1')

        for contest_id in range(self.number_of_participated_contests):
            response = self.client.get(reverse('contest-info', kwargs={'contest_pk': contest_id + 1}))
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'contests/info.html')


class ContestRankingViewTest(TestCase):
    number_of_participants = 10

    @classmethod
    def setUpTestData(cls):
        contest = Contest.objects.create(title='Contest 1', start_time=timezone.now(),
                                         end_time=timezone.now() + timezone.timedelta(hours=5))

        for participant_id in range(cls.number_of_participants):
            user = User.objects.create_user(
                'user' + str(participant_id+1),
                'user' + str(participant_id+1) + '@test.com',
                'password' + str(participant_id+1)
            )
            contest.participant_set.create(user=user, points=10 * (participant_id - (participant_id % 2)))

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get('/contest/1/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('contest-ranking', kwargs={'contest_pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_requires_authentication(self):
        response = self.client.get(reverse('contest-ranking', kwargs={'contest_pk': 1}))
        self.assertRedirects(response, reverse('login-page') + '?login-page=/contest/1/ranking/')

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('contest-ranking', kwargs={'contest_pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/ranking.html')

    def test_view_lists_all_participants(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('contest-ranking', kwargs={'contest_pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['participants']), self.number_of_participants)

    def test_view_lists_participants_sorted_by_points(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('contest-ranking', kwargs={'contest_pk': 1}))

        self.assertEqual(response.status_code, 200)

        last_points = 0
        for participant in reversed(response.context['participants']):
            self.assertTrue(participant.points >= last_points)
            last_points = participant.points
