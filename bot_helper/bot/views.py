from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models.AliceResponse import AliceResponse
from .models.AliceEvent import AliceEvent

HOST = "http://localhost:8001"

def get_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text":text, "tts":tts}

        
        
def about_campuses(event, *args, **kwargs):
    return AliceResponse(event, "В ИТМО есть 5 корпусов")

def about_campus(event, campus, field=None, *args, **kwargs):
    link = f"{HOST}/gsheet/campuses/?campus={campus}&top"
    campuses = requests.get(link).json()
    pharse = get_phrase(campuses[0], field="phrase")
    response = AliceResponse(event, **pharse)
    return response

def fallback(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event, "Извините, непонятно")

def about_apps(event, *args, **kwargs):
    text= """
    Я могу рассказать про:\n\n
    1. my.itmo\n
    2. ИСУ\n
    3. itmo.students\n
    4. itmo.map\n\n
    Что интересует?
    """
    tts = "Я могу рассказать про май итм+о. ИС+У. итм+о сть+юденс и итм+о мэп. Что интересует?"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks=["about_app_enum"])
    response.to_state("callback", "about_app_enum")
    return response


def enum(link, offset):
    array = requests.get(link).json()
    try:
        if offset == len(array)-1:
            return [array[offset]]
        return [array[offset], array[offset+1]]
    except IndexError:
        return []
    

def about_app_enum(event, app="isu", init=False, *args, **kwargs):
    link = f"{HOST}/gsheet/apps/?app={app}&top"
    offset = event.state.get("offset", 0)
    if init:
        offset = 0
    apps = enum(link=link, offset=offset)
    if apps:
        phrase = get_phrase(apps[0], "phrase")
        response = AliceResponse(event=event, **phrase, intent_hooks=["YANDEX.CONFIRM"])
        if len(apps) == 2:
            response.add_text("Интересно узнать про ещё одно приложение?")
            response.to_state("callback", "about_app_enum")
            response.to_state("offset", offset+1)
        if len(apps) == 1:
             response.add_text("Приложений больше нет")
        return response
        

def repeat(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text=event.state["text"], tts=event.state["tts"], state=event.state, repeat=True)


def confirm(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text="Заглушка на согласие")




INTENTS = {
    'about_campuses':  about_campuses,
    'about_campus': about_campus,
    'about_apps': about_apps,
    'YANDEX.REPEAT': repeat,
    'YANDEX.CONFIRM': confirm,
    'confirm': confirm,
    'about_app_enum': about_app_enum
}

CALLBACKS = {
    'about_app_enum': about_app_enum,
}


class BotHandler(APIView):
    def post(self, request):
        event = AliceEvent(request=request)
        intent, slots = event.get_intent()

        if event.intent_hooks and event.callback:
            if intent in event.intent_hooks:
                print("ОТВЕТ НА ИНТЕНТ")
                print(event.slots)
                return Response(INTENTS[event.callback](event, **event.slots)(intent, slots=event.slots))

        if intent:
            try:
                print("ОБЩИЙ ИНТЕНТ")
                return Response(INTENTS[intent](event, init=True, **slots)(screen=intent, slots=slots))
            except KeyError as e:
                return Response(fallback(event=event)("fallback"))
        else:
            return Response(AliceResponse(event, "Привет, как дела?")("Hello"))
