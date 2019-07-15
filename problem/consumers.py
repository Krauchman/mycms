from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from channels.db import database_sync_to_async

from submission.models import RunInfo, RunSubtaskInfo
from problem.models import Test
from contest.models import Contest, Participant
from contest.serializers import UserSerializer, ParticipantSerializer

from django.core import serializers


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = 'users_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify(self, event):
      sub_id = event['sub_id']
      sub_status = event['status']
      sub_points = event['points']
      # Send message to WebSocket

      if sub_status == 0:
          sub_status = 'In queue...'
      elif sub_status == 1:
          sub_status = 'Compiling...'
      elif sub_status == 2:
          sub_status = 'Compilation Error'
      elif sub_status == 3:
          sub_status = 'Testing...'
      elif sub_status == 4:
          sub_status = 'Finished'
      elif sub_status == 5:
          sub_status = 'Error occured'
      
      context = {
          'submission_pk': str(sub_id),
          'status': sub_status,
          'sub_points': sub_points,
          'type': 'sub_notify'
      }

      await self.send(text_data=json.dumps(context))

    async def test_checked(self, event):
      message = event['message']
      time_consumed = event['time']
      test_id = event['test_id']
      attr = event['attr']
      # Send message to WebSocket
      context = {
          'type': 'run_info',
          'message': message,
          'time': time_consumed,
          'test_id': test_id,
          'attr': attr
      }

      await self.send(text_data=json.dumps(context))

    @database_sync_to_async
    def getInfos(self, submission_pk, subtask_id):
        return RunInfo.objects.filter(submission__pk=submission_pk, test__subtask__subtask_id=subtask_id)

    @database_sync_to_async
    def getPtsInfos(self, submission_pk):
        return RunSubtaskInfo.objects.filter(submission__pk=submission_pk)

    async def get_info(self, text_data_json):
        data = await self.getInfos(text_data_json['submission'], text_data_json['subtask'])
        test_ids = []

        for info in data:
            test_ids.append(info.test.test_id)

        data = serializers.serialize("json", data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_infos',
                'data': data,
                'test_ids': test_ids,
                'attr': "#info_{}_{}".format(text_data_json['submission'], text_data_json['subtask'])
            }
        )

    async def getPtsInfo(self, text_data_json):
        data = await self.getPtsInfos(text_data_json['submission'])
        sub_desc = []

        for info in data:
            sub_desc.append(info.subtask.pk)
        
        data = serializers.serialize("json", data)
        # test_ids = serializers.serialize("json", test_ids)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_pts_infos',
                'data': data,
                'sub_desc': sub_desc,
                'attr': "#subtaskPts_{}_".format(text_data_json['submission'])
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if text_data_json['type'] == 'get_info':
            await self.get_info(text_data_json)
        elif text_data_json['type'] == 'getSubtasksPtsInfo':
            await self.getPtsInfo(text_data_json)

    # Receive message from room group
    async def send_infos(self, event):
        data = event['data']
        attr = event['attr']
        test_ids = event['test_ids']

        # Send message to WebSocket
        context = {
            'type': 'runInfos',
            'data': data,
            'attr': attr,
            'test_ids': test_ids
        }

        await self.send(text_data=json.dumps(context))
    
    async def send_pts_infos(self, event):
        data = event['data']
        attr = event['attr']
        sub_desc = event['sub_desc']

        # Send message to WebSocket
        context = {
            'type': 'subtaskPtsInfos',
            'data': data,
            'attr': attr,
            'sub_desc': sub_desc
        }

        await self.send(text_data=json.dumps(context))

class RankingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['contest_pk']
        self.room_group_name = 'ranking_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def getProblem(self):
        return Contest.objects.filter(pk=int(self.room_name)).first().problem_set.all()
    @database_sync_to_async
    def getParticipant(self):
        return Participant.objects.filter(contest__pk=int(self.room_name))

    async def getAllRanking(self):
        contestData = await self.getProblem()
        participantData = await self.getParticipant()
        contestData = serializers.serialize("json", contestData)
        participantData = ParticipantSerializer(instance=participantData)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'sendAllRanking',
                'contestData': contestData,
                'participantData': participantData,
            }
        )
    async def sendAllRanking(self, event):
        context = {
            'type': 'rankingAll',
            'contestData': event['contestData'],
            'participantData': event['participantData'],
        }
        await self.send(text_data=json.dumps(context))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'getRanking':
            await self.getAllRanking()
