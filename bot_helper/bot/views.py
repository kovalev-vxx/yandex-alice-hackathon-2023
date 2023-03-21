from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import apps_getter, campuses_getter, campus_questions_getter, faq_getter, discounts_getter

# from bot_helper.utils import get_data_from_xlsx
from .structure.AliceResponse import AliceResponse
from .structure.AliceEvent import AliceEvent



def build_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text": text, "tts": tts}


def about_coworkings(event, *args, **kwargs):
    text = """
    Коворкинги есть в следующих корпусах:

    - Ломоносова
    - Кронверкский
    - Биржевая линия
    - Чайковского

    Какой корпус интересует? 🤔
    """
    tts = """
    Ков+оркинги есть в сл+едующих корпус+ах:

    - Ломон+осова.
    - Кр+онверкский.
    - Биржев+ая линия.
    - Чайк+овского.

    Какой корпус интересует?
    """
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_campus_enum", "about_campus_enum":"about_campus_enum"})




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
    return response


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
    

def about_app_enum(event, app="isu", offset=0, number=-1, init=False, *args, **kwargs):
    if init:
        offset = 0

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


def about_faq(event, object_faq='name_rector', offset=0, topic=None, init=False, *args, **kwargs):
    """
    params:
    event - parsed request
    object_faq - FAQ name
    offset - step of list
    topic - category of discount
    return:
    response
    """
    if init:
        offset = 0

    objects_faq = faq_getter(offset, object_faq, topic)
    if objects_faq:
        phrase = build_phrase(objects_faq[0], "answer")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM": "about_faq"})
        if len(objects_faq) == 2:
            response.add_text(objects_faq[1]['bot_question'])
            response.to_slots("offset", offset+1)
        if len(objects_faq) == 1:
            response.add_text("Что еще хочешь узнать?")
            response.intent_hooks = {}
        return response


def about_discounts(event, title='Планетарий 1', offset=0, category=None, init=False, *args, **kwargs):
    """
    params:
    event - parsed request
    title - title name
    offset - step of list
    category - category of discount
    return:
    response
    """
    if init:
        offset = 0

    discounts = discounts_getter(offset, title, category)
    print(discounts[0])
    if discounts:
        phrase = build_phrase(discounts[0], "description")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM": "about_discounts"})
        if len(discounts) == 2:
            response.add_text(discounts[offset+1]['bot_question'])
            response.to_slots("offset", offset+1)
        if len(discounts) == 1:
            response.add_text("Что еще хочешь узнать?")
            response.intent_hooks = {}
        return response
    # return AliceResponse(title, 'sss')


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
    'about_apps': about_apps,
    'YANDEX.REPEAT': repeat,
    'YANDEX.CONFIRM': confirm,
    'numbers': numbers,
    'confirm': confirm,
    'about_app_enum': about_app_enum,
    'about_faq': about_faq,
    'about_discounts': about_discounts,
}


class BotHandler(APIView):
    def post(self, request):
        event = AliceEvent(request=request)
        intent, slots = event.get_intent()
        print(intent, slots)
        if intent:
            try:
                if event.intent_hooks:
                    try:
                        slots = {**event.slots, **slots}
                        print("ЧАСТНЫЙ ИНТЕНТ")
                        return Response(INTENTS[event.intent_hooks[intent]](event, **slots)(intent, slots=slots))
                    except KeyError as e:
                        print(e)
                print("ОБЩИЙ ИНТЕНТ")
                return Response(INTENTS[intent](event, init=True, **slots)(screen=intent, slots=slots))
            except KeyError as e:
                return Response(fallback(event=event)("fallback"))
        else:
            return Response(AliceResponse(event, "Привет, как дела?")("Hello"))
