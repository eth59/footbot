import requests
import csv

def generate_standings():
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }

    url = "https://v3.football.api-sports.io/leagues"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    for league in data['response']:
        if league['league']['name'] == 'Ligue 1' and league['country']['code'] == 'FR':
            for season in league['seasons']:
                if season['current']:
                    id_ligue_1 = league['league']['id']
                    
    url = f"https://v3.football.api-sports.io/standings?league={id_ligue_1}&season=2022"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    standings = data['response'][0]['league']['standings'][0]
    header = ['Rang', 'Club', 'MJ', 'G', 'N', 'P', 'BP', 'BC', 'DB', 'Pts', '5 derniers']
    with open('l1_standings.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for line in standings:
            rank = line['rank']
            club = line['team']['name']
            mj = line['all']['played']
            g = line['all']['win']
            n = line['all']['draw']
            p = line['all']['lose']
            bp = line['all']['goals']['for']
            bc = line['all']['goals']['against']
            db = line['goalsDiff']
            pts = line['points']
            last5 = line['form']
            writer.writerow([rank, club, mj, g, n, p, bp, bc, db, pts, last5])
