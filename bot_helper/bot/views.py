from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from bot_helper.utils import get_data_from_xlsx
from .models.AliceResponse import AliceResponse
from .models.AliceEvent import AliceEvent

HOST = "http://localhost:8001"

def get_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text":text, "tts":tts}

def about_campuses(event, *args, **kwargs):
    text = """
    Всего у ИТМО есть 5 основных корпусов:\n\n
    1. Ломоносова\n
    2. Кронверкский\n
    3. Биржевая линия\n
    4. Гривцова\n
    5. Чайковского\n\n
    О каком хочешь узнать побольше?
    """
    tts = "Всего у ИТМ+О есть 5 основных корпусов: Ломоносова. Кронверкский.Биржевая линия.Гривцова.Чайковского. О каком хочешь узнать побольше?"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_campus_enum", "about_campus_enum":"about_campus_enum"})
    response.to_state("callback", "about_campus_enum")
    return response

def about_campus_enum(event, campus="kronva", number=None, init=False, field=None, *args, **kwargs):
    print("FIELD", field)
    campuses = ["lomo", "kronva", "birga", "griva", "chaika"]
    try:
        campus = campuses[number-1]
    except:
        pass
    link = f"{HOST}/gsheet/campuses/?campus={campus}&top"
    offset = event.state.get("offset", 0)
    if init:
        offset = 0
    campuses = enum(link=link, offset=offset)
    if campuses:
        if field:
            return about_campus_enum_details(event, campuses)
        phrase = get_phrase(campuses[0], "phrase")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_campus_enum_details"})
        if len(campuses) == 2:
            response.add_text("Интересно узнать про историю?")
            response.to_state("callback", "about_campus_enum_details")
            response.to_state("field", "history")
            response.to_state("offset", offset+1)
        if len(campuses) == 1:
             response.add_text("Приложений больше нет")
        return response

def about_campus_enum_details(event, campus, field):
    print(campus)
    return AliceResponse(event, "Заглушка вопроса про корпус")


def about_apps(event, *args, **kwargs):
    text= """
    Я могу рассказать про:\n\n
    1. my.itmo\n
    2. itmo.map\n
    3. ИСУ\n
    4. itmo.students\n\n
    Что интересует?
    """
    tts = "Я могу рассказать про май итм+о. итм+о мэп. ИС+У. и итм+о сть+юденс  Что интересует?"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_app_enum", "about_app_enum":"about_app_enum"})
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
    

def about_app_enum(event, app="isu", number=None, init=False, *args, **kwargs):
    apps = ["my_itmo", "itmo_map", "ISU", "itmo_students"]
    try:
        app = apps[number-1]
    except:
        pass
    link = f"{HOST}/gsheet/apps/?app={app}&top"
    offset = event.state.get("offset", 0)
    if init:
        offset = 0
    apps = enum(link=link, offset=offset)
    if apps:
        phrase = get_phrase(apps[0], "phrase")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_app_enum"})
        if len(apps) == 2:
            response.add_text("Интересно узнать про ещё одно приложение?")
            response.to_state("callback", "about_app_enum")
            response.to_state("offset", offset+1)
        if len(apps) == 1:
             response.add_text("Приложений больше нет")
             response.intent_hooks = {}
        return response

        

def repeat(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text=event.state["text"], tts=event.state["tts"], state=event.state, repeat=True)


def confirm(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text="Заглушка на согласие")

def fallback(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event, "Извините, непонятно")

def numbers(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text="Заглушка на число")




INTENTS = {
    'about_campuses':  about_campuses,
    'about_campus_enum': about_campus_enum,
    'about_apps': about_apps,
    'YANDEX.REPEAT': repeat,
    'YANDEX.CONFIRM': confirm,
    'numbers': numbers,
    'confirm': confirm,
    'about_campus_enum_details': about_campus_enum_details,
    'about_app_enum': about_app_enum
}


class BotHandler(APIView):
    def post(self, request):
        event = AliceEvent(request=request)
        intent, slots = event.get_intent()
        print(slots)
        print(event.intent_hooks)
        

        if intent:
            try:
                if event.intent_hooks:
                    slots = {**slots, **event.slots}
                    return Response(INTENTS[event.intent_hooks[intent]](event, **slots)(intent, slots=slots))
                print("ОБЩИЙ ИНТЕНТ")
                return Response(INTENTS[intent](event, init=True, **slots)(screen=intent, slots=slots))
            except KeyError as e:
                return Response(fallback(event=event)("fallback"))
        else:
            return Response(AliceResponse(event, "Привет, как дела?")("Hello"))
