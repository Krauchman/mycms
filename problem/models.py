from django.db import models
from contest.models import Contest
import requests
import time
import hashlib
import string
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

from sandbox.sandbox_manager import Sandbox

class Problem(models.Model):
    problem_id = models.IntegerField(default=0)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    testset_name = models.CharField(max_length=100, default="tests")
    contest = models.ManyToManyField(Contest, blank=True)
    def __str__(self):
        return str(self.problem_id)


class Test(models.Model):
    input = models.TextField()
    test_id = models.IntegerField()
    in_statement = models.BooleanField(default=False)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.problem.problem_id) + '-' + str(self.test_id)

    class Meta:
        order_with_respect_to = 'test_id'

class Statement(models.Model):
    legend = models.TextField()
    input = models.TextField()
    output = models.TextField()
    notes = models.TextField()
    name = models.CharField(max_length=100)
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    input_file = models.CharField(max_length=100)
    output_file = models.CharField(max_length=100)

    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.name)

api_url = "https://polygon.codeforces.com/api/"

def param_config(params):
    for key in list(params.keys()):
        if key not in ['apiKey', 'apiSig', 'time', 'problemId']:
            params.pop(key, None)

def gen_hash():
    return ''.join(random.choices(string.ascii_uppercase + string.digits+ string.ascii_lowercase, k=6))

def api_sig(method, secret, add):
    api_hash = gen_hash()
    signature = api_hash + '/' + method
    started = False
    for key, value in add:
        if started is False:
            signature = signature + '?'
        else:
            signature = signature + '&'
        signature = signature + key + '=' + value
        started = True
    signature = signature + '#' + secret
    return api_hash + hashlib.sha512(str(signature).encode('utf-8')).hexdigest()

def get_statement(params, instance, Time):
    param_config(params)
    method = 'problem.statements'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    return requests.get(api_url + method, params).json()

def get_info(params, instance, Time):
    param_config(params)
    method = 'problem.info'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    return requests.get(api_url + method, params).json()

def get_test(params, instance, Time):
    param_config(params)
    method = 'problem.tests'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('testset', instance.testset_name), ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    params['testset'] = instance.testset_name
    return requests.get(api_url + method, params).json()

def generate_test(params, instance, Time, scriptLine):
    param_config(params)
    name = scriptLine.split()[0] + '.cpp'
    method = 'problem.viewFile'
    my_params = [('apiKey', str(instance.key)), ('name', name), ('problemId', str(instance.problem_id)),
                ('time', Time), ('type', 'source')]
    params['type'] = 'source'
    params['name'] = name
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    gen_code = requests.get(api_url + method, params).text
    print(gen_code)

@receiver(post_save, sender=Problem)
def get_problem_data(sender, instance, created, **kwargs):
    Time = str(int(time.time()))
    params = {
        'apiKey': instance.key,
        'time': Time,
        'problemId': instance.problem_id,
    }

    statement = get_statement(params, instance, Time)
    info = get_info(params, instance, Time)
    tests = get_test(params, instance, Time)
    for test in tests['result']:
        if test['manual'] is True:
            instance.test_set.create(input=test['input'], test_id=test['index'], in_statement=test['useInStatements'])
        else:
            generate_test(params, instance, Time, test['scriptLine'])
    
    cur_statement = Statement(legend=statement['result']['russian']['legend'],
                                  input=statement['result']['russian']['input'],
                                  output=statement['result']['russian']['output'],
                                  notes=statement['result']['russian']['notes'],
                                  name=statement['result']['russian']['name'], time_limit=info['result']['timeLimit'],
                                  memory_limit=info['result']['memoryLimit'],
                                  input_file=info['result']['inputFile'], output_file=info['result']['outputFile'])
    if created == False:
        Statement.objects.get(name=instance.statement.name).delete()
    instance.statement = cur_statement.save()