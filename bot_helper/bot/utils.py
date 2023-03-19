import requests

HOST = "http://localhost:8001"

def get_phrase(_object, field):
    text = _object.get(field, "")
    tts = _object.get(f"{field}_tts", text)
    return {"text":text, "tts":tts}

def enum(link, offset):
    array = requests.get(link).json()
    try:
        if offset == len(array)-1:
            return [array[offset]]
        return [array[offset], array[offset+1]]
    except IndexError:
        return []  