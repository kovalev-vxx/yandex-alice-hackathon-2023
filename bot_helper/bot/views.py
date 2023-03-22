from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import apps_getter, campuses_getter, campus_questions_getter, faq_getter, discounts_getter, coworking_getter, help_getter

# from bot_helper.utils import get_data_from_xlsx
from .structure.AliceResponse import AliceResponse, Button
from .structure.AliceEvent import AliceEvent
from random import choice as randomchoice
from random import seed


def common_intent(event, text=None, tts=None, show_text=True, *args, **kwargs):

    _text = "Всегда рад помочь! Рассказать подробнее, что я умею?"
    _tts = "Всегда рад помочь! Рассказать подробнее, что я умею?"

    if not text:
        _text= """Как и всякий кошачий, очень мудрый и много чего знаю.\n\nМогу рассказать подробно о корпусах Университета ИТМО, коворкингах, приложениях и скидках. Обращайся!\n\nЗнаю очень много сокращений! Спокойно спрашивай про "Ломо" или "Кронву" – я пойму! Рассказать подробнее что я умею?"""
        _tts = "Интересно, что я еще умею?"

    if not show_text:
        _text=""
        _tts=""

    if text:
        _text = f"{text}\n\n{_text}"
    
    if tts:
        _tts = f"{tts}\n\n{_tts}"

    init_response = AliceResponse(event, text=_text, tts=tts, intent_hooks={'YANDEX.CONFIRM':'help_intent'})
    init_response.to_slots("offset", 0)
    init_response.add_txt_buttons(['Скидки', 'Приложения','Коворкинги','Корпуса'])
    return init_response


def build_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text": text, "tts": tts}


def about_coworkings(event, *args, **kwargs):
    

    text = """
    Коворкинги есть в следующих корпусах:

    1. Ломоносова
    2. Кронверкский
    3. Биржевая линия
    4. Чайковского

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
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_coworking_enum"})
    return response


def about_coworking_enum(event, campus='lomo', number=-1, offset=0, init=False,  *args, **kwargs):
    if init:
        offset=0

    campuses = ['lomo', 'kronva', 'birga', 'chaika']
    if (number-1) in range(len(campuses)):
        campus = campuses[number-1]

    coworkings = coworking_getter(offset=offset, campus=campus)
    if coworkings:
        phrase = build_phrase(coworkings[0], 'phrase')
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_coworking_enum"})
        if len(coworkings) == 2:
            response.add_text(randomchoice(["Найти ещё коворкинг здесь?", "Рассказать о еще одном коворкинге здесь?", "Рассказать о ещё одном?"]))
            response.to_slots("offset", offset+1)
        if len(coworkings) == 1:
            phrase['text'] = f"""{phrase['text']}\n\nВ корпусе больше нет коворкингов."""
            phrase['tts'] = f"""{phrase['tts']} В корпусе больше нет ков+оркингов."""
            return common_intent(event, **phrase)
        return response
    pass


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


def about_campus_enum(event, campus='lomo', number=-1, init=False, question_offset=0, offset=0, *args, **kwargs):
    if init:
        offset=0
        question_offset=0

    campuses = ['lomo', 'kronva', 'birga', 'chaika']
    if (number-1) in range(len(campuses)):
        campus = campuses[number-1]

    
    questions = campus_questions_getter(offset=question_offset)
    campuses = campuses_getter(offset=offset, campus=campus)
    if campuses:
        phrase = build_phrase(campuses[0], 'phrase')
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_campus_details", "YANDEX.REJECT":"reject_campus_details"})
        if len(campuses) == 2:
            question_phrase = build_phrase(questions[0], 'question')
            response.add_text(**question_phrase)
            response.to_slots("campus", campus)
            response.to_slots("field", questions[0]['field'])
            response.to_slots("offset", offset+1)
        if len(campuses) == 1:
            question_phrase = build_phrase(questions[0], 'question')
            response.add_text(**question_phrase)
            response.to_slots("campus", campus)
            response.to_slots("field", questions[0]['field'])
            response.to_slots("offset", offset+1)
        return response

def reject_campus_details(event, offset=0, *args, **kwargs):
    text = "Хочешь узнать про другие корпуса?"
    tts = "Хочешь узнать про другие корпус+а?"
    if offset==5:
            return common_intent(event, "Больше ничего не знаю про корпуса.")
    return AliceResponse(event=event, text=text, tts=tts, intent_hooks={"YANDEX.CONFIRM":"about_campus_enum"})

def about_campus_details(event, campus='lomo', field='history', init=False, question_offset=0, offset=0, *args, **kwargs):
    if init:
        question_offset=0
        offset=0
    questions = campus_questions_getter(offset=question_offset, field=f"{field}")
    campus = campuses_getter(offset=0, campus=campus)[0]
    
    if questions:
        phrase = build_phrase(campus, questions[0]['field'])
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_campus_details", "YANDEX.REJECT":"reject_campus_details"})
        if len(questions) == 2:
            question_phrase = build_phrase(questions[1], 'question')
            response.add_text(**question_phrase)
            response.to_slots("question_offset", question_offset+1)
            if offset == 0:
                response.to_slots("offset", 1)
                response.to_slots("campus", campus)
        if len(questions) == 1:
            response.add_text("Это все, что я знаю про этот корпус, рассказать про другой?")
            response.intent_hooks = {"YANDEX.CONFIRM":"about_campus_enum"}
        return response
    return AliceResponse(event=event, text='about_campus_details')





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
            phrase['text'] = f"""{phrase['text']}\n\nПриложений больше нет."""
            phrase['tts'] = f"""{phrase['tts']} Приложений больше нет."""
            return common_intent(event, **phrase)
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

    if topic is None:
        objects_faq = faq_getter(offset, object_faq)
        topic = objects_faq[0]['topic']

    objects_faq = faq_getter(offset, object_faq, topic)
    if objects_faq:
        phrase = build_phrase(objects_faq[0], "answer")
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM": "about_faq"})
        if len(objects_faq) == 2:
            response.add_text(objects_faq[1]['bot_question'])
            response.to_slots("offset", offset+1)
            response.to_slots("topic", objects_faq[0]['topic'])
        if len(objects_faq) == 1:
            response.add_text("Что еще хочешь узнать?")
            response.intent_hooks = {}
        return response
    # return AliceResponse(event, "test faq")


# Discounts
def about_discounts_start(event, *args, **kwargs):
    text = """
    Можешь спросить про скидки около какого-либо корпуса или по категориям:\n
    - Развлечения 🕹️\n
    - Спорт 💪\n
    - Еда 🍔\n
    - Здоровье 🏥\n
    - Учеба 💻\n
    Что интересует? 🤔
    """
    tts = """
    Можешь спросить про скидки около какого-либо корпуса или по следующим категориям. Развлечения, Спорт, Еда, Здоровье, Учеба. Что интересует?
    """
    response = AliceResponse(event=event, text=text, tts=tts,
                             intent_hooks={"YANDEX.CONFIRM": "about_discounts_category",
                                           "YANDEX.REJECT": "YANDEX.REJECT",
                                           "about_discounts": "about_discounts"}, init=True)
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

def reject(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text="Заглушка на отказ")

def help_intent(event:AliceEvent, offset=0, init=False, *args, **kwargs):
    seed(offset)
    text = ""

    if init:
        offset=0
        text = "Барс всегда придет на помощь!\n\nЯ могу много чего. Расскажу по порядку:"

    guide = help_getter(offset=offset)


    if guide:
        phrase = build_phrase(guide[0], "guide")
        phrase['text'] = f"""{text}\n\n{phrase['text']}"""
        phrase['tts'] = f"""{text}\n\n{phrase['tts']}"""
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"help_intent"})
        if len(guide) == 2:
            response.add_text(randomchoice(["Интересно, что я ещё умею?", "Рассказать, что я ещё умею?"]))
            response.to_slots("offset", offset+1)
        if len(guide) == 1:
            phrase['text'] = f"""{phrase['text']}\n\nОбращайся! Повторить ещё раз, что я умею?"""
            phrase['tts'] = f"""{phrase['tts']}Обращайся! Повторить ещё раз, что я умею?"""
            return common_intent(event, **phrase, show_text=False)
        return response


    return AliceResponse(event=event, text=text)


INTENTS = {
    'about_campuses':  about_campuses,
    'about_apps': about_apps,
    'YANDEX.REPEAT': repeat,
    'YANDEX.CONFIRM': confirm,
    'YANDEX.REJECT': reject,
    'numbers': numbers,
    'confirm': confirm,
    'about_app_enum': about_app_enum,
    'about_faq': about_faq,
    'about_coworkings': about_coworkings,
    'about_coworking_enum': about_coworking_enum,
    'about_campus_enum':about_campus_enum,
    'about_campus_details':about_campus_details,
    'reject_campus_details':reject_campus_details,
    'reject_campus_details':reject_campus_details,
    'YANDEX.HELP':help_intent,
    'help_intent': help_intent,
    'YANDEX.WHAT_CAN_YOU_DO' : common_intent,
    'about_discounts_start': about_discounts_start,
    'about_discounts': about_discounts,
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
                        print("ЧАСТНЫЙ ИНТЕНТ")
                        return Response(INTENTS[event.intent_hooks[intent]](event, **slots)(intent, slots=slots))
                    except KeyError as e:
                        print("ОШИБКА")
                        print(e)
                print("ОБЩИЙ ИНТЕНТ")
                return Response(INTENTS[intent](event, init=True, **slots)(screen=intent, slots=slots))
            except KeyError as e:
                return Response(fallback(event=event)("fallback"))
        else:
            return Response(AliceResponse(event, "Привет, как дела?")("Hello"))