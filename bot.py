import requests
class Bot:
    token = "6855019928:AAEwiBxbXooXcCHReh2NvEmgMXma7bjwpUI"
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        
    def get_updates(self, offset=None):
        method = "getUpdates"
        params = {'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result = resp.json()
        return result
    
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = "sendMessage"
        resp = requests.post(self.api_url + method, params).json()
        return resp
    