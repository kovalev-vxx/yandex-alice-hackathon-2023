import requests

from parser.views import get_from_excel_local

def enum_validate(link, offset):
    array = requests.get(link).json()
    try:
        if offset == len(array)-1:
            return [array[offset]]
        return [array[offset], array[offset+1]]
    except IndexError:
        return []

def enum_validate_local(res, offset):
    try:
        if offset == len(res)-1:
            return [res[offset]]
        return [res[offset], res[offset+1]]
    except IndexError:
        return []


def apps_getter(offset, app=None):
    res = get_from_excel_local({'app':app}, sheet="apps", top=True)
    return enum_validate_local(res=res, offset=offset)


def campuses_getter(offset, campus=None):
    res = get_from_excel_local({'campus':campus}, sheet="campuses", top=True)
    return enum_validate_local(res=res, offset=offset)


def campus_questions_getter(offset, field=None):
    res = get_from_excel_local({'field':field}, sheet="campus_questions", top=True)
    return enum_validate_local(res=res, offset=offset)



def faq_getter(offset, object_faq=None, topic=None):
    res = get_from_excel_local({'object_faq':object_faq, 'topic': topic}, filterby='topic', sheet="FAQ", top=True)
    return enum_validate_local(res=res, offset=offset)

def discounts_getter(offset, category=None, campus=None, top=True):
    res = get_from_excel_local({'category':category, 'campus': campus}, sheet="discounts", top=top)
    return enum_validate_local(res=res, offset=offset)

    

def coworking_getter(offset, campus=None, top=False):
    res = get_from_excel_local({'campus':campus}, sheet="coworkings", top=top)
    return enum_validate_local(res=res, offset=offset)

def help_getter(offset):
    res = get_from_excel_local({}, sheet="guide", top=True)
    return enum_validate_local(res=res, offset=offset)