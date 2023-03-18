from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import json
import requests

def make_response(text, tts=None):
    return {
        'response': {
            'text': text,
            'tts': tts if tts is not None else text,
        },
        'version': '1.0',
    }

def about_campuses(*args, **kwargs):
    return make_response("В ИТМО есть 5 корпусов")

def about_campus(campus, field=None, *args, **kwargs):
    response = requests.get(f"http://localhost:8000/gsheet/campuses/?campus={campus}&top").json()
    return make_response(text=response[0]['phrase'], tts=response[0]['phrase_tts'])

def fallback(event, *args, **kwargs):
    return make_response("Извините, непонятно")

INTENTS = {
    'about_campuses':  about_campuses,
    'about_campus': about_campus
}


class BotHandler(APIView):
    def post(self, request):
        event = json.loads(request.body.decode('utf-8'))
        _intents = event['request'].get('nlu', {}).get('intents')
        _intents = list(_intents.items())
        if _intents:
            intent = _intents[0][0]
            slots = {}
            for key, value in _intents[0][1]['slots'].items():
                slots[key] = value["value"]
            try:
                return Response(INTENTS[intent](**slots))
            except KeyError:
                return Response(fallback(event))
        else:
            return Response(make_response("Привет, как дела?"))



