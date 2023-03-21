from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import apps_getter, campuses_getter, campus_questions_getter

from bot_helper.utils import get_data_from_xlsx
from .structure.AliceResponse import AliceResponse
from .structure.AliceEvent import AliceEvent

HOST = "http://localhost:8001"

def build_phrase(_object, field):
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

def about_campus_enum(event, campus="kronva", offset=0, number=-1, question_offset=0, field=None, *args, **kwargs):
    campuses = ["lomo", "kronva", "birga", "griva", "chaika"]
    if (number-1) in range(len(campuses)):
        campus = campuses[number-1]
    campuses = campuses_getter(offset=offset, campus=campus)
    questions = campus_questions_getter(offset=question_offset, field=field)
    if campuses:
        if field:
            #зачитать поле и предложить следующий вопрос
            return about_campus_enum_details(event, campus, field)
        phrase = build_phrase(campuses[0], "phrase")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_campus_enum_details"})
        if len(campuses) == 2:
            response.add_text("Интересно узнать про историю?")
            response.to_slots("field", "history")
            response.to_slots("offset", offset+1)
        if len(campuses) == 1:
             response.add_text("Приложений больше нет")
        return response

#TODO: Добавить получение вопросов по корпусам, написать логику и интента
#Если сказать нет, до откидывает обратно в кампусы
#Назвать здесь offset не offset, а question_offset, чтобы остался offset про кампуc
def about_campus_enum_details(event, campus, field, question_offset=0, *args, **kwargs):
    questions = campus_questions_getter(offset=question_offset, field=field)
    if questions:
        phrase = build_phrase(questions[0], "question")
        return AliceResponse(event, **phrase)
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
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_app_enum", "about_app_enum":"about_app_enum"}, init=True)
    return response
    

def about_app_enum(event, app="isu", offset=0, number=-1, *args, **kwargs):
    apps = ["my_itmo", "itmo_map", "ISU", "itmo_students"]
    if (number-1) in range(len(apps)):
        app = apps[number-1]
    apps = apps_getter(offset=offset, app=app)
    if apps:
        phrase = build_phrase(apps[0], "phrase")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_app_enum"})
        if len(apps) == 2:
            response.add_text("Интересно узнать про ещё одно приложение?")
            response.to_slots("offset", offset+1)
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

        if intent:
            try:
                if event.intent_hooks:
                    try:
                        slots = {**event.slots, **slots}
                        return Response(INTENTS[event.intent_hooks[intent]](event, **slots)(intent, slots=slots))
                    except:
                        pass
                print("ОБЩИЙ ИНТЕНТ")
                return Response(INTENTS[intent](event, **slots)(screen=intent, slots=slots))
            except KeyError as e:
                return Response(fallback(event=event)("fallback"))
        else:
            return Response(AliceResponse(event, "Привет, как дела?")("Hello"))
