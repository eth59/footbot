import requests
import csv
import sqlite3

def generate_standings():
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }            
    url = f"https://v3.football.api-sports.io/standings?league=61&season=2022"
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
            

def get_match(domicile, exterieur):
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }
    url = "https://v3.football.api-sports.io/fixtures?league=61&season=2022"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    for match in data['response']:
        if (match['teams']['home']['name'] == domicile and
            match['teams']['away']['name'] == exterieur):
            return match
        

def get_team_list():
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }
    url = "https://v3.football.api-sports.io/teams?league=61&season=2022"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    team_list = []
    for team in data['response']:
        team_list.append(team['team']['name'])
    return team_list


def update_bdd():
    try:
        conn = sqlite3.connect('prono.db')
        cursor = conn.cursor()
        payload={}
        headers = {
            'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
        }
        url = "https://v3.football.api-sports.io/fixtures?league=61&season=2022"
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        for match in data['response']:
            domicile = match['teams']['home']['name']
            exterieur = match['teams']['away']['name']
            cursor.execute("""
            SELECT id_match, butDomicile, butExterieur, commence FROM matchs
            WHERE domicile = ? AND exterieur = ?
            """, (domicile, exterieur))
            score = cursor.fetchone()
            if score[3] == 0:
                if match['fixture']['status']['short'] not in ['TBD', 'NS', 'PST']:                    
                    cursor.execute("""
                    UPDATE matchs
                    SET commence = 1
                    WHERE id_match = ?
                    """, (score[0],))
                    conn.commit()
                
            if (score[1] is None and score[2] is None
                and match['goals']['home'] is not None 
                and match['goals']['away'] is not None
                and match['fixture']['status']['short'] == 'FT'):
                
                butD = match['goals']['home']
                butE = match['goals']['away']
                cursor.execute("""
                UPDATE matchs
                SET butDomicile = ?, butExterieur = ?
                WHERE id_match = ?
                """, (butD, butE, score[0]))
                conn.commit()

                cursor.execute("""
                SELECT * FROM pronos WHERE id_match = ?
                """, (score[0],))
                pronos = cursor.fetchall()
                for prono in pronos:
                    if ((prono[2] == prono[3] and butD == butE) or
                        (prono[2] < prono[3] and butD < butE) or
                        (prono[2] > prono[3] and butD > butE)):
                        points_win = 100
                    else:
                        points_win = 20
                    if (abs(prono[2]-prono[3]) == abs(butD-butE)):
                        points_win += 50
                    if (prono[2]==butD and prono[3]==butE):
                        points_win += 100
                        
                    cursor.execute("""
                    SELECT points FROM users WHERE id_user = ?
                    """, (prono[1],))
                    points = cursor.fetchone()
                    cursor.execute("""
                    UPDATE users
                    SET points = ?
                    WHERE id_user = ?
                    """, (points[0]+points_win, prono[1]))
                    conn.commit()
                        
    except Exception as e:
        raise e
    finally:
        conn.close()
        

def nickname(name):
    if name.lower() == 'losc':
        return 'Lille'
    elif name.lower() == 'ol':
        return 'Lyon'
    elif name.lower() == 'om':
        return 'Marseille'
    elif name.lower() == 'psg':
        return 'Paris Saint Germain'
    elif name.lower() == 'tfc':
        return 'Toulouse'
    elif name.lower() == 'clermont':
        return 'Clermont Foot'
    elif name.lower() == 'brest' or name.lower() == 'stade brestois':
        return 'Stade Brestois 29'
    elif name.lower() == 'troyes':
        return 'Estac Troyes'
    elif name.lower() == 'rcl':
        return 'Lens'
    else:
        return name.title()
    
    
def get_remaining_requests():
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }
    url = "https://v3.football.api-sports.io/status"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return data['response']['requests']['limit_day'] - data['response']['requests']['current']


def get_points():
    try:
        conn = sqlite3.connect('prono.db')
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT pseudo, points FROM users
        """)
        res = cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()
    return res


def get_journee(numero):
    payload={}
    headers = {
        'x-apisports-key': 'dc155322ba6c5a28850ada669a659f34'
    }
    url = "https://v3.football.api-sports.io/fixtures?league=61&season=2022"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    res = []
    for match in data['response']:
        if "Regular Season - "+str(numero) == match['league']['round']:
            dom = match['teams']['home']['name']
            ext = match['teams']['away']['name']
            butDom = match['goals']['home']
            butExt = match['goals']['away']
            date = match['fixture']['date']
            jour = date[8:10]
            mois = date[5:7]
            annee = date[:4]
            heure = date[11:16]
            timezone = match['fixture']['timezone']
            status = match['fixture']['status']['short']
            res.append((dom, ext, butDom, butExt, jour, mois, annee, heure, timezone, status))
    return res