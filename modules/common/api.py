import requests
import json
import pprint

class ApiControlller:
    def get(self, url, params={}):
        res = requests.get(url, params)
        data = json.loads(res.text)
        #pprint.pprint(data)
        return data

