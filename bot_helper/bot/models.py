import requests

HOST = "http://localhost:8001"


def enum_validate(link, offset):
    array = requests.get(link).json()
    try:
        if offset == len(array)-1:
            return [array[offset]]
        return [array[offset], array[offset+1]]
    except IndexError:
        return []


def apps_getter(offset, app=None):
    link = f"{HOST}/gsheet/apps/?app={app}&top"
    return enum_validate(link=link, offset=offset)


def campuses_getter(offset, campus=None):
    link = f"{HOST}/gsheet/campuses/?campus={campus}&top"
    return enum_validate(link=link, offset=offset)


def campus_questions_getter(offset, field=None):
    link = f"{HOST}/gsheet/campus_questions/?field={field}&top"
    return enum_validate(link=link, offset=offset)


def faq_getter(offset, object_faq=None, topic=None):
    link = f"{HOST}/gsheet/FAQ/?object_faq={object_faq}&topic={topic}&top"
    return enum_validate(link=link, offset=offset)


def discounts_getter(offset, title=None, category=None):
    link = f"{HOST}/gsheet/discounts/?title={title}&category={category}&top"
    return enum_validate(link=link, offset=offset)

def coworking_getter(offset, campus=None):
    link = f"{HOST}/gsheet/coworkings?campus={campus}"
    return enum_validate(link=link, offset=offset)