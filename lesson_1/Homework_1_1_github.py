import requests
import json
from pprint import pprint

# https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api
# https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user
# RUS examples - https://pyneng.github.io/pyneng-3/GitHub-API-JSON-example/

# Auth information
auth_username = 'Mike-Orlov'
auth_token = ''

username = 'boston-dynamics' # Name of the user whose repos to parse
url_user_repos = f'https://api.github.com/users/{username}/repos'

params = {'sort':'updated'}
# "We encourage you to explicitly request v3 version via the Accept header"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}

# Create a re-usable session object with the user creds in-built
# It allows you to persist certain parameters and cookies across requests and will use urllib3’s connection pooling. 
# So if you’re making several requests to the same host, the underlying TCP connection will be reused, 
# which can result in a significant performance increase.
gh_session = requests.Session()
gh_session.auth = (auth_username, auth_token)
gh_session.headers.update({'Accept': 'application/vnd.github.v3+json'})

# GET request
# Nearly all requests in production code should be made with timeout parameter
# Failure to do so can cause your program to hang indefinitely
response = gh_session.get(url_user_repos, headers=headers, params=params, timeout=1)
# An exception is raised if the server has not issued a response for timeout seconds
# Example: requests.exceptions.Timeout: HTTPConnectionPool(host='github.com', port=80): Request timed out. (timeout=0.001)

# print(type(response)) # "response" is an object of <class 'requests.models.Response'>

# Converting string to JSON
j_data = response.json()
#pprint(j_data)

for repo in j_data:
    print(repo['name'])

with open('user_repos.json', 'w', encoding='utf-8') as f:
    json.dump(j_data, f, ensure_ascii=False, indent=4)