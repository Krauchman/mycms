from django.db import models
from django.contrib.auth.models import User

from contest.models import Contest
from problem.models import Problem, Test


class Submission(models.Model):
    class STATUS:
        IN_QUEUE = 0
        COMPILING = 1
        COMPILATION_ERROR = 2
        TESTING = 3
        FINISHED = 4
        ERROR = 5
        DESC = [
            "In queue...",
            "Compiling...",
            "Compilation error",
            "Testing...",
            "Finished",
            "System error",
        ]

    class LANGUAGE:
        CPP17 = 0

    source = models.TextField(blank=True)
    language = models.SmallIntegerField(default=LANGUAGE.CPP17)
    status = models.SmallIntegerField(default=STATUS.IN_QUEUE)
    current_test = models.IntegerField(default=0)

    sent_date = models.DateTimeField(auto_now_add=True, null=True)

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.pk) + '-' + str(self.status)

    def message(self):
        return Submission.STATUS.DESC[self.status]


class RunInfo(models.Model):
    class STATUS:
        # TODO add ML
        OK = 0
        WA = 1
        TL = 2
        WTL = 3
        RE = 4
        PE = 5
        NA = 6
        XX = 7
        DESC = [
            "OK",
            "Wrong answer",
            "Time limit exceeded",
            "Wall-clock time limit exceeded",
            "Runtime error",
            "Presentation error",
            "N/A",
            "System error",
        ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    status = models.SmallIntegerField(default=STATUS.NA)
    time = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.submission.pk) + '-' + str(self.test.test_id)

    def message(self):
        return RunInfo.STATUS.DESC[self.status]
