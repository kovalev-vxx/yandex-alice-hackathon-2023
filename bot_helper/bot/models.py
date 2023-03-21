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

