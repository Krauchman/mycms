from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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


# class ContestInfoViewTest(TestCase):
#     number_of_contests = 10
#     number_of_active_contests = 8
#
#     @classmethod
#     def setUpTestData(cls):
#         for contest_id in range(cls.number_of_contests):
#             Contest.objects.create(
#                 title='Contest ' + str(contest_id),
#                 start_time=timezone.now() + timezone.timedelta(minutes=contest_id*30),
#                 end_time=timezone.now() + timezone.timedelta(hours=contest_id),
#                 is_active=(contest_id < cls.number_of_active_contests)
#             )
#
#     def test_view_url_exists_at_desired_location(self):
#         for contest_id in range(self.number_of_active_contests):
#             response = self.client.get(reverse('contest-info', kwargs={'contest_pk': contest_id+1}))
#             print(reverse('contest-info', kwargs={'contest_pk': contest_id+1}))
#             self.assertEqual(response.status_code, 200)
#
#     def test_view_url_accessible_by_name(self):
#         response = self.client.get(reverse('main-page'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_view_uses_correct_template(self):
#         response = self.client.get(reverse('main-page'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'contests/contest_list.html')
#
#     def test_view_lists_all_contests(self):
#         response = self.client.get(reverse('main-page'))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context['contest_list']), self.number_of_active_contests)



