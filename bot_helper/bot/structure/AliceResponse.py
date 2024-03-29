from ..structure.AliceEvent import AliceEvent

class Button:
    def __init__(self, title, url=None, hide=True):
        self.title = title
        self.url = url
        self.hide = hide
    

class AliceResponse:
    def __init__(self, event:AliceEvent, text, tts=None, state=None, end_session=False, repeat=False, intent_hooks={}, init=False) -> None:
        self.state = {}
        self.text = text
        self.tts = tts if tts is not None else text
        self.event = event
        self.repeat = repeat
        self.end_session = False
        self.intent_hooks = intent_hooks
        self.slots = {}
        self.init = init
        self.buttons = []
        self.end_session = end_session
        
    def __call__(self, screen, slots={}):
        if self.repeat:
            return self.repeat_response()

        response = {
            'text': self.text,
            'tts': self.tts,
            'buttons': self.buttons,
            "end_session": self.end_session,
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
    
    def add_button(self, button:Button):
        self.buttons.append({'title':button.title, 'url':button.url, 'hide':button.hide})
    
    def add_buttons(self, buttons):
        for button in buttons:
            self.add_button(button)

    def add_txt_buttons(self, texts):
        for text in texts:
            self.add_button(Button(text))