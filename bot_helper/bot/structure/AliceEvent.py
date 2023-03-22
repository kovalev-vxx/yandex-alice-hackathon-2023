import json

class AliceEvent:
    def __init__(self, request):
        self.event = json.loads(request.body.decode('utf-8'))
        self.intents = list(self.event['request'].get('nlu', {}).get('intents').items())
        self.session = self.event["session"]
        self.state = self.event.get("state", {}).get("session", {})
        self.callback = self.state.get("callback", None)
        self.intent_hooks = self.state.get("intent_hooks", None)
        self.slots = self.state.get("slots", {})
        self.new = self.session["new"]
        self.user_id = self.session["user"]["user_id"]
    
    def get_state(self):
        return self.state

    def get_intent(self):
        if not self.intents:
            return None, None
        intent = self.intents[0][0]
        slots = {}
        for key, value in self.intents[0][1]['slots'].items():
            slots[key] = value["value"]
        return intent, slots