from os.path import join as path_join

from celery import shared_task
from billiard import current_process

from .models import Submission, RunInfo, RunSubtaskInfo, RunFullInfo
from sandbox.sandbox_manager import Sandbox

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from problem.consumers import UserConsumer

from django.core import serializers


def get_meta(sandbox, meta_file):
    content = sandbox.get_file(meta_file).split('\n')
    content = list(line for line in content if line)

    meta = dict()
    for line in content:
        key, val = line.split(':')
        meta[key] = val

    return meta


def run_solution(sandbox, name, problem_constraints, test):
    sandbox.create_file(str(problem_constraints.input_file), str(test.input), file_dir='box')
    sandbox.create_file(str(problem_constraints.output_file), '', file_dir='box')
    sandbox.run_exec(name, dirs=[('/box', 'box', 'rw')], meta_file=sandbox.get_box_dir('meta'),
                     stdin_file=str(problem_constraints.input_file), stdout_file=str(problem_constraints.output_file),
                     time_limit=problem_constraints.time_limit, memory_limit=problem_constraints.memory_limit)


def clear_submission(sub):
    if hasattr(sub, 'runinfo_set'):
        sub.runinfo_set.all().delete()
    sub.points = 0
    sub.current_test = 0
    Submission.objects.filter(pk=sub.pk).update(points=0, current_test=0)

def status_socket(channel_name, context):
    async_to_sync(get_channel_layer().group_send)(channel_name, context)

def getPtsInfo(channel_name, submission_pk):
        data = RunSubtaskInfo.objects.filter(submission__pk=submission_pk)
        sub_desc = []

        for info in data:
            sub_desc.append(info.subtask.pk)
        
        data = serializers.serialize("json", data)

        context = {
            'type': 'send_pts_infos',
            'data': data,
            'sub_desc': sub_desc,
            'attr': "#subtaskPts_{}_".format(submission_pk)
        }

        async_to_sync(get_channel_layer().group_send)(channel_name, context)

@shared_task
def evaluate_submission(sub_pk, username=None):
    """ Evaluate or re-evaluate submission """

    sub = Submission.objects.get(pk=sub_pk)

    clear_submission(sub)

    sandbox = Sandbox()
    sandbox.init(current_process().index)

    sub.status = Submission.STATUS.COMPILING
    sub.save()
    if username:
        status_socket("users_%s" % username, {
        "type": "notify",
        "sub_id": sub_pk,
        "status": sub.status,
        "points": sub.points
        })
    # Compiling
    sandbox.create_file('main.cpp', str(sub.source), is_public=0)
    out, err = sandbox.run_cmd('g++ -o ' + path_join('box', 'main') + ' -std=c++11 -DONLINE_JUDGE main.cpp')
    if err != b'' or out != b'':
        sub.status = Submission.STATUS.COMPILATION_ERROR
        sub.save()
        if username:
            status_socket("users_%s" % username, {
            "type": "notify",
            "sub_id": sub_pk,
            "status": sub.status,
            "points": sub.points
            })
        return

    sub.status = Submission.STATUS.TESTING
    sub.save()
    if username:
        status_socket("users_%s" % username, {
        "type": "notify",
        "sub_id": sub_pk,
        "status": sub.status,
        "points": sub.points
        })

    # TODO properly access static files
    with open(path_join('.', 'submission', 'static', 'submission', 'testlib.h'), 'r') as testlib_file:
        testlib = testlib_file.read()

    sandbox.create_file('testlib.h', str(testlib), is_public=0)
    sandbox.create_file('check.cpp', str(sub.problem.checker), is_public=0)
    out, err = sandbox.run_cmd('g++ -o check -std=c++11 check.cpp testlib.h')
    if err != b'':
        print(err.decode('utf-8'))
        sub.status = Submission.STATUS.ERROR
        sub.save()
        if username:
            status_socket("users_%s" % username, {
            "type": "notify",
            "sub_id": sub_pk,
            "status": sub.status,
            "points": sub.points
            })
        return

    problem_constraints = sub.problem.statement
    if not sub.is_invocation:
        participant = sub.participant
        if participant.submission_set.filter(problem=sub.problem).order_by('-points'):
            participant.points -= participant.submission_set.filter(problem=sub.problem).order_by(
                '-points').first().points
    isFull = True
    for subtask in sub.problem.subtask_set.order_by('subtask_id'):
        cur_points = subtask.points
        for test in subtask.test_set.order_by('test_id'):
            sub.current_test = test.test_id
            sub.save()
            if username:
                status_socket("users_%s" % username, {
                "type": "notify",
                "sub_id": sub_pk,
                "status": sub.status,
                "points": sub.points
                })
            run_solution(sandbox, 'main', problem_constraints, test)

            meta = get_meta(sandbox, 'meta')

            run_info = sub.runinfo_set.filter(test=test)
            if run_info:
                run_info = run_info.first()
            else:
                run_info = sub.runinfo_set.create(test=test)

            if 'status' not in meta:
                run_info.output = sandbox.get_file(path_join('box', problem_constraints.output_file))
                if sub.is_invocation:
                    run_info.status = RunInfo.STATUS.OK
                    run_info.time = float(meta['time'])
                    test.output = run_info.output
                    inputBR = test.input.count("\n")
                    outputBR = test.output.count("\n")
                    br_numberInput = max(0, outputBR - inputBR)
                    br_numberOutput = max(0, inputBR - outputBR)
                    for _ in range(br_numberInput):
                        test.input += "\r\n"
                    for _ in range(br_numberOutput):
                        test.output += "\r\n"
                    test.save()
                else:
                    ans_file = 'test.a'
                    sandbox.create_file(ans_file, str(test.output), is_public=0)
                    out, err, code = sandbox.run_cmd('./check ' +
                                                     path_join('.', 'box', str(problem_constraints.input_file)) + ' ' +
                                                     path_join('.', 'box', str(problem_constraints.output_file)) + ' ' +
                                                     path_join('.', ans_file), with_code=True)
                    if code == 0:
                        run_info.status = RunInfo.STATUS.OK
                    elif code == 1:
                        run_info.status = RunInfo.STATUS.WA
                    elif code == 2:
                        run_info.status = RunInfo.STATUS.PE
                    elif code == 3:
                        run_info.status = RunInfo.STATUS.CF
                    run_info.time = float(meta['time'])
            elif meta['status'] == 'TO':
                if meta['message'] == 'Time limit exceeded':
                    run_info.status = RunInfo.STATUS.TL
                else:
                    run_info.status = RunInfo.STATUS.WTL
                run_info.time = float(problem_constraints.time_limit)
            elif meta['status'] == 'SG' or meta['status'] == 'RE':
                run_info.status = RunInfo.STATUS.RE
                run_info.time = float(meta['time'])
            else:
                run_info.status = RunInfo.STATUS.XX
            if run_info.status != RunInfo.STATUS.OK:
                cur_points = 0
                isFull = False
            run_info.save()
            if username:
                status_socket("users_%s" % username, {
                "type": "test_checked",
                "test_id": run_info.test.test_id,
                "message": run_info.message(),
                "time": run_info.time,
                "attr": "#info_{}_{}".format(sub.pk, subtask.subtask_id),
                })
        sub.points += cur_points
        if not RunSubtaskInfo.objects.filter(submission=sub, subtask=subtask):
            RunSubtaskInfo.objects.create(submission=sub, subtask=subtask)
        RunSubtaskInfo.objects.filter(submission=sub, subtask=subtask).update(points=cur_points)
        if username:
             getPtsInfo("users_%s" % username, sub.pk)
        sub.save()
    sub.status = Submission.STATUS.FINISHED
    sub.save()

    if username:
        status_socket("users_%s" % username, {
        "type": "notify",
        "sub_id": sub_pk,
        "status": sub.status,
        "points": sub.points
        })

    if not sub.is_invocation:
        participant.points += participant.submission_set.filter(problem=sub.problem).order_by('-points').first().points
        participant.save()

        active = True
        if RunFullInfo.objects.filter(full=True,problem=sub.problem,participant=participant):
            active = False
        RunFullInfo.objects.create(submission=sub, problem=sub.problem,participant=participant,points=sub.points,isFull=isFull,active=active)
    sandbox.cleanup()
