import requests

url = 'http://127.0.0.1:8000/parse'
files = {'file': open('SEP2025_AA03366523_TXN.pdf','rb')}
resp = requests.post(url, files=files)
print('status', resp.status_code)
try:
    j = resp.json()
    print('json keys:', list(j.keys()) if isinstance(j, dict) else type(j))
    # print truncated holdings count
    if isinstance(j, dict) and 'holdings' in j:
        print('holdings count:', len(j['holdings']))
except Exception as e:
    print('response text:', resp.text)
