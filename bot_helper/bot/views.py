from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import apps_getter, campuses_getter, campus_questions_getter, faq_getter, discounts_getter, coworking_getter, help_getter

# from bot_helper.utils import get_data_from_xlsx
from .structure.AliceResponse import AliceResponse, Button
from .structure.AliceEvent import AliceEvent
from random import choice as randomchoice
from random import seed
import users.models as user_models
import users.serializers as user_serializers


def common_intent(event, text=None, tts=None, show_text=True, *args, **kwargs):

    _text = "Я очень много чего знаю! Рассказать подробнее, что умею?"
    _tts = "Я очень много чего знаю! Рассказать подробнее, что умею?"



    if not text:
        _text= """Как и всякий кошачий, я очень мудрый и много чего знаю.\n\nМогу рассказать подробно о корпусах Университета ИТМО, коворкингах, приложениях и скидках. Обращайся!\n\nЗнаю очень много сокращений! Спокойно спрашивай про "Ломо" или "Кронву" – я пойму! Рассказать подробнее что я умею?"""
        _tts = """Как и всякий кошачий, я очень мудрый и много чего знаю.\n\nМогу рассказать подробно о корпусах Университета ИТМ+О, коворкингах, приложениях и скидках. Обращайся!\n\nЗнаю очень много сокращений! Спокойно спрашивай про "Л+омо" или "Кр+онву" – я пойму! Рассказать подробнее что я умею?"""
    

    if not show_text:
        _text=""
        _tts=""

    if text:
        _text = f"{text}\n\n{_text}"
    
    if tts:
        _tts = f"{tts}\n\n{_tts}"


    init_response = AliceResponse(event, text=_text, tts=_tts, intent_hooks={'YANDEX.CONFIRM':'help_intent'})
    init_response.to_slots("offset", 0)
    init_response.add_txt_buttons(['Да', 'Скидки', 'Приложения','Коворкинги','Корпуса'])
    return init_response


def build_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text": text, "tts": tts}


def hello_intent(event, new_user=False, *args, **kwargs):
    text = "Привет! Я Барс - твой МегаАдаптер в ИТМО!\n\nС возвращением! 😁\n\nНапомнить, что умею? 🤔"
    if new_user:
        text = "Привет! Я Барс - твой МегаАдаптер в ИТМО!\n\nЯ талисман университета с 2013 года, очень много о нем знаю и с радостью поделюсь с тобой!\n\nРассказать, что я умею?"
    response = AliceResponse(event=event, text=text, intent_hooks={'YANDEX.CONFIRM':'common_intent'})
    response.add_txt_buttons(['Да', 'Скидки', 'Приложения','Коворкинги','Корпуса'])
    return response

def goodby_intent(event, *args, **kwargs):
    return AliceResponse(event=event, text="До скорых встреч!", end_session=True)



def about_coworkings(event, *args, **kwargs):
    

    text = "Коворкинги есть в следующих корпусах:\n\n1. Ломоносова\n2. Кронверкский\n3. Биржевая линия\n4. Чайковского\n\nКакой корпус интересует? 🤔"
    tts = """
    Ков+оркинги есть в сл+едующих корпус+ах:

    - Ломон+осова.
    - Кр+онверкский.
    - Биржев+ая линия.
    - Чайк+овского.

    Какой корпус интересует?
    """
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_coworking_enum", "about_campus_enum":"about_coworking_enum"})
    response.add_txt_buttons(['Ломоносова', 'Кронверкский', 'Биржевая линия', 'Чайковского'])
    return response


def about_coworking_enum(event, campus='lomo', number=-1, offset=0, init=False,  *args, **kwargs):
    if init:
        offset=0

    campuses = ['lomo', 'kronva', 'birga', 'chaika']
    if (number-1) in range(len(campuses)):
        campus = campuses[number-1]

    coworkings = coworking_getter(offset=offset, campus=campus, top=True)
    if coworkings:
        phrase = build_phrase(coworkings[0], 'phrase')
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_coworking_enum"})
        if len(coworkings) == 2:
            response.add_text(randomchoice(["Найти ещё коворкинг здесь?", "Рассказать о еще одном коворкинге здесь?", "Рассказать о ещё одном?"]))
            response.to_slots("offset", offset+1)
            response.add_txt_buttons(['Да'])
        if len(coworkings) == 1:
            phrase['text'] = f"{phrase['text']}\n\nВ корпусе больше нет коворкингов."
            phrase['tts'] = f"{phrase['tts']} В корпусе больше нет ков+оркингов."
            return common_intent(event, **phrase)
        return response
    pass


def about_campuses(event, *args, **kwargs):
    text = "Всего у ИТМО есть 5 основных корпусов:\n\n1. Ломоносова\n2. Кронверкский\n3. Биржевая линия\n4. Гривцова\n5. Чайковского\n\nО каком хочешь узнать побольше?"
    tts = "Всего у ИТМ+О есть 5 основных корпусов: Ломоносова. Кронверкский.Биржевая линия.Гривцова.Чайковского. О каком хочешь узнать побольше?"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_campus_enum", "about_campus_enum":"about_campus_enum"})
    response.add_txt_buttons(['Ломоносова', 'Кронверкский', 'Биржевая линия', 'Гривцова', 'Чайковского'])
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
            response.add_txt_buttons(['Да'])
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
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"YANDEX.CONFIRM":"about_campus_enum"})
    response.add_txt_buttons(['Да'])
    return response

def about_campus_details(event, campus='lomo', field='history', init=False, question_offset=0, offset=0, *args, **kwargs):
    if init:
        question_offset=0
        offset=0
    questions = campus_questions_getter(offset=question_offset, field=f"{field}")
    campus = campuses_getter(offset=0, campus=campus)[0]
    
    if questions:
        phrase = build_phrase(campus, questions[0]['field'])
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_campus_details", "YANDEX.REJECT":"reject_campus_details"})
        response.add_txt_buttons(['Да'])
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
    text= "Я могу рассказать про:\n\n1. my.itmo\n2. itmo.map\n3. ИСУ\n4. itmo.students\n\nЧто интересует?"
    tts = "Я могу рассказать про май итм+о. итм+о мэп. ИС+У. и итм+о сть+юденс  Что интересует?"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_app_enum"})
    response.add_txt_buttons(['my.itmo', 'itmo.map', 'ИСУ', 'itmo.students'])
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
            response.add_txt_buttons(['Да'])
        if len(apps) == 1:
            phrase['text'] = f"{phrase['text']}\n\nПриложений больше нет."
            phrase['tts'] = f"{phrase['tts']} Приложений больше нет."
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
        topic = None

    if topic is None:
        objects_faq = faq_getter(offset, object_faq)
        topic = objects_faq[0]['topic']
    print(object_faq, topic)
    objects_faq = faq_getter(offset, object_faq, topic)
    if objects_faq:
        phrase = build_phrase(objects_faq[0], "answer")
        print(phrase)
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM": "about_faq"})
        if len(objects_faq) == 2:
            question = build_phrase(objects_faq[1], "bot_question")
            response.add_text(**question)
            response.to_slots("offset", offset + 1)
            if offset==0:
                response.to_slots("topic", topic)
        elif len(objects_faq) == 1:
            phrase['text'] = f"{phrase['text']}\n\nФух, на этом у меня все..."
            phrase['tts'] = f"{phrase['tts']} Фух, на этом у меня все..."
            return common_intent(event, **phrase)
        return response


def about_discounts(event, *args, **kwargs):
    text = "Можешь спросить про скидки около какого-либо корпуса или по категориям:\n\n1. Развлечения 🕹️\n2. Спорт 💪 \n3. Еда 🍔\n4. Здоровье 🏥 \n5. Учеба 💻\n\nЧто интересует? 🤔"
    tts = "Можешь спросить про скидки около какого-либо корпуса или по категориям:\n\nРазвлечения. 🕹️Спорт. 💪Еда. 🍔Здоровье. 🏥 Учеба. 💻\n\nЧто интересует? 🤔"
    response = AliceResponse(event=event, text=text, tts=tts, intent_hooks={"numbers":"about_discounts_by_category", "about_campus_enum":"about_discounts_campus"})
    response.add_txt_buttons(["у Ломоносова","Еда", "Спорт", "Еда", "Здоровье", "Учеба"])
    return response

def about_discounts_by_category(event, campus=None, category="food", number=-1, offset=0, init=False, *args, **kwargs):
    seed(offset)
    if init:
        offset=0

    categories = ["rest", "sport", "food", "health", "edu"]
    if (number-1) in range(len(categories)):
        categories = categories[number-1]

    discounts = discounts_getter(offset=offset, category=category, campus=campus)
    if discounts:
        phrase = build_phrase(discounts[0], 'phrase')
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_discounts_by_category"})
        if len(discounts) == 2:
            response.add_text(randomchoice(["Найти еще скидки в этой категории?"]))
            response.to_slots("offset", offset+1)
            response.to_slots("link", discounts[0]["link"])
            response.to_slots("prev_intent", 'about_discounts_by_category')
            link = discounts[0]["link"]
            if link != "-":
                response.add_button(Button("Ссылка", discounts[0]["link"]))
            response.add_txt_buttons(['Да'])
        if len(discounts) == 1:
            phrase['text'] = f"{phrase['text']}\n\nБольше нет скидок в этой категории."
            phrase['tts'] = f"{phrase['tts']} Больше нет скидок в этой категории."
            return common_intent(event, **phrase)
        return response
    pass

def about_discounts_campus(event, campus="lomo", category="food", init=False, offset=0, *args, **kwargs):
    seed(offset)
    if init:
        offset=0

    discounts = discounts_getter(offset=offset, category=category, campus=campus)
    if discounts:
        phrase = build_phrase(discounts[0], 'phrase')
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"about_discounts_campus"})
        if len(discounts) == 2:
            response.add_text(randomchoice(["Найти ещё скидки рядом с этим корпусом?", "Найти ещё скидки поблизости?"]))
            response.to_slots("offset", offset+1)
            response.to_slots("link", discounts[0]["link"])
            response.to_slots("prev_intent", 'about_discounts_campus')
            link = discounts[0]["link"]
            if link != "-":
                response.add_button(Button("Ссылка", discounts[0]["link"]))
            response.add_txt_buttons(['Да'])
        if len(discounts) == 1:
            phrase['text'] = f"{phrase['text']}\n\nБольше нет скидок рядом."
            phrase['tts'] = f"{phrase['tts']} Больше нет скидок рядом."
            return common_intent(event, **phrase)
        return response
    pass

    return AliceResponse(event, f"о скидках у места {campus}")

def link(event, link, prev_intent, *args, **kwargs):
    text = f"{link}\n\nНайти ещё скидку?"
    tts = f"Найти ещё скидку?"
    response = AliceResponse(event, text, tts, intent_hooks={"YANDEX.CONFIRM":prev_intent})
    response.add_txt_buttons(['Да'])
    return response

def repeat(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event=event, text=event.state["text"], tts=event.state["tts"], state=event.state, repeat=True)

def fallback(event:AliceEvent, *args, **kwargs):
    return AliceResponse(event, "Извините, непонятно")

def reject(event:AliceEvent, *args, **kwargs):
    return common_intent(event, text="Если захочешь выйти, скажи \"Пока\" или \"Хватит\"")

def help_intent(event:AliceEvent, offset=0, init=False, *args, **kwargs):
    seed(offset)
    text = ""

    if init:
        offset=0
        text = "Барс всегда придет на помощь!\n\nЯ могу много чего. Расскажу по порядку:"

    guide = help_getter(offset=offset)


    if guide:
        phrase = build_phrase(guide[0], "guide")
        phrase['text'] = f"{text}\n\n{phrase['text']}"
        phrase['tts'] = f"{text}\n\n{phrase['tts']}"
        response = AliceResponse(event=event, **phrase, intent_hooks={"YANDEX.CONFIRM":"help_intent"})
        if len(guide) == 2:
            response.add_text(randomchoice(["Интересно, что я ещё умею?", "Рассказать, что я ещё умею?"]))
            response.add_txt_buttons(['Да', 'Скидки', 'Приложения','Коворкинги','Корпуса'])
            response.to_slots("offset", offset+1)
        if len(guide) == 1:
            phrase['text'] = f"{phrase['text']}\n\nОбращайся! Повторить ещё раз, что я умею?"
            phrase['tts'] = f"{phrase['tts']}Обращайся! Повторить ещё раз, что я умею?"
            return common_intent(event, **phrase, show_text=False)
        return response


    return AliceResponse(event=event, text=text)


INTENTS = {
    'about_campuses':  about_campuses,
    'about_apps': about_apps,
    'YANDEX.REPEAT': repeat,
    'YANDEX.REJECT': reject,
    'about_app_enum': about_app_enum,
    'about_faq': about_faq,
    'about_discounts': about_discounts,
    'about_coworkings': about_coworkings,
    'about_coworking_enum': about_coworking_enum,
    'about_campus_enum':about_campus_enum,
    'about_campus_details':about_campus_details,
    'reject_campus_details':reject_campus_details,
    'YANDEX.HELP':help_intent,
    'help_intent': help_intent,
    'YANDEX.WHAT_CAN_YOU_DO' : common_intent,
    'repeat': repeat,
    'hello_intent': hello_intent,
    'common_intent': common_intent,
    'goodby_intent': goodby_intent,
    'about_discounts_by_category':about_discounts_by_category,
    'about_discounts_campus': about_discounts_campus,
    'about_discounts_by_category': about_discounts_by_category,
    'link':link
}


class BotHandler(APIView):
    def post(self, request):
        event = AliceEvent(request=request)
        intent, slots = event.get_intent()

        if event.new:
            try:
                user = get_object_or_404(user_models.User, alice_user_id=event.user_id)
                return Response(hello_intent(event=event, new_user=False)(screen="hello"))
            except:
                serializer = user_serializers.UserSerializer(data={"alice_user_id":event.user_id, "name":"unknown"})
                if serializer.is_valid():
                    serializer.save()
                return Response(hello_intent(event=event, new_user=True)(screen="hello"))


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
            text = "Я тебя не понял 🤔\n\nРассказать, что умею?"
            tts = "Я тебя не понял.\n\nРассказать, что умею?"
            response = AliceResponse(event, text=text, tts=tts, intent_hooks={'YANDEX.CONFIRM':'common_intent'})
            response.add_txt_buttons(["Да"])
            return Response(response("don't understand"))
