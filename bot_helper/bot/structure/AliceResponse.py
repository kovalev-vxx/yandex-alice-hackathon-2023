from ..structure.AliceEvent import AliceEvent


class AliceResponse:
    def __init__(self, event:AliceEvent, text, tts=None, state=None, repeat=False, intent_hooks={}, init=False) -> None:
        self.state = {}
        self.text = text
        self.tts = tts if tts is not None else text
        self.event = event
        self.repeat = repeat
        self.end_session = False
        self.intent_hooks = intent_hooks
        self.slots = {}
        self.init = init
        
    def __call__(self, screen, slots={}):
        if self.repeat:
            return self.repeat_response()

        response = {
            'text': self.text,
            'tts': self.tts,
            "end_session": False,
        }

        webhook_response = {
        'response': response,
        'version': '1.0'
        }
        self.state["text"] = self.text
        self.state["tts"] = self.tts
        self.state["end_session"] = self.end_session
        self.state["screen"] = screen
        self.state["intent_hooks"] = self.intent_hooks

        if self.init:
            self.state["slots"] = self.slots
        else:
            self.state["slots"] = {**slots, **self.slots}
        


    
        webhook_response["session_state"] = self.state
        return webhook_response
    
    def repeat_response(self):
        response = {
                'text': self.event.state["text"],
                'tts': self.event.state["tts"],
                'end_session': self.event.state["end_session"],
            }
        webhook_response = {
        'response': response,
        # 'session': self.event.session,
        'version': '1.0'
        }
        webhook_response["session_state"] = self.event.state
        return webhook_response
        
    
    def add_text(self, text, tts=None):
        self.text += f"\n\n{text}"
        if tts:
            self.tts += f" {tts}"
        else:
            self.tts += f" {text}"
    
    def to_state(self, key, value):
        self.state[key] = value
    
    def to_slots(self, key, value):
        self.slots[key] = value

    def set_callback(self, callback):
        self.state["callback"] = callback