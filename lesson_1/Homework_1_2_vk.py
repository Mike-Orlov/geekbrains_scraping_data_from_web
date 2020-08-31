import requests
import json
from pprint import pprint

method_name = 'users.getSubscriptions'
url = f'https://api.vk.com/method/{method_name}'

access_token = ''
params = {'v':'5.52', 'access_token':access_token, 'user_id':23403, 'extended':1} # Extended - расширенный вывод, опционально
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}

# Sessions can also be used as context managers:
with requests.Session() as gh_session:
    response = gh_session.get(url, headers=headers, params=params)
# This will make sure the session is closed as soon as the with block is exited, even if unhandled exceptions occurred.

groups_list = []
if response.status_code == requests.codes.ok:
    j_data = response.json()
#    pprint(j_data)
    for names in j_data['response']['items']:
        groups_list.append(names['name'])
else:
    print(f'Sorry, something went wrong')

print(groups_list)

with open('groups_list.rtf', 'w', encoding='utf-8') as f:
    f.writelines(groups_list)