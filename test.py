import requests

payload={}
headers = {
    'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
}
url = "https://v3.football.api-sports.io/fixtures?league=61&season=2022"
response = requests.request("GET", url, headers=headers, data=payload)
data = response.json()
print(data['response'])